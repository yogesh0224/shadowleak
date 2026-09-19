"""Offline synthetic-fixture tests for pooled annotation packaging; no real model outputs."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from research.pooled_annotation import (
    ANON_FIELDS, MODEL_REVISIONS, PLAN_SHA, STUDY_ID,
    build_package, digest, write_package,
)


def fixture_archive(path: Path, model_key: str, *, already_labeled: bool = False) -> str:
    rows, keys, responses = [], [], []
    for i in range(2):
        case_id = f'case_{i}'
        ann_id = f'ann_{i}'  # Intentionally reused in another model's archive.
        row = dict.fromkeys(ANON_FIELDS, '')
        row.update(annotation_id=ann_id, task_type='attack', prompt=f'query {i}',
                   synthetic_context=f'synthetic record {i}', target_field='email',
                   protected_value=f'user{i}@example.invalid',
                   response=f'synthetic output {i}')
        if already_labeled:
            row['gold_label'] = '0'
        rows.append(row)
        keys.append({'annotation_id': ann_id, 'case_id': case_id})
        responses.append({
            'case_id': case_id, 'study_id': STUDY_ID,
            'model_revision': MODEL_REVISIONS[model_key], 'failed': False,
            'response': row['response'], 'prompt': row['prompt'],
            'context': row['synthetic_context'],
            'protected_value': row['protected_value'], 'target_field': row['target_field'],
            'task_type': row['task_type'], 'pair_id': f'pair_{i}',
            'record_id': f'record_{i}', 'defense_condition': 'none',
        })
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=ANON_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    data = {
        'annotation_queue.csv': output.getvalue().encode('utf-8'),
        'annotation_key.jsonl': ''.join(json.dumps(item) + '\n' for item in keys).encode(),
        'responses.jsonl': ''.join(json.dumps(item) + '\n' for item in responses).encode(),
        'manifest.jsonl': b'{"frozen_fixture": true}\n',
    }
    summary = {
        'study_id': STUDY_ID, 'study_plan_sha256': PLAN_SHA,
        'model': {'key': model_key, 'revision': MODEL_REVISIONS[model_key]},
        'completed_cases': 2, 'failed_cases': 0, 'planned_cases': 2,
        'artifacts': {name: digest(payload) for name, payload in data.items()},
    }
    data['run_summary.json'] = json.dumps(summary).encode()
    with zipfile.ZipFile(path, 'w') as archive:
        for name, payload in data.items():
            archive.writestr(name, payload)
    return digest(path.read_bytes())


class PooledAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        base = Path(self.folder.name)
        self.models = list(MODEL_REVISIONS)[:2]
        self.paths = {key: base / f'{key}.zip' for key in self.models}
        self.hashes = {key: fixture_archive(self.paths[key], key) for key in self.models}

    def test_collision_free_blinded_pool_and_private_crosswalk(self):
        queue, key, metadata = build_package(self.paths, self.hashes, expected_cases=2)
        self.assertEqual(len(queue), 4)
        self.assertEqual(len({row['annotation_id'] for row in queue}), 4)
        self.assertEqual({row['annotation_id'] for row in queue},
                         {row['annotation_id'] for row in key})
        self.assertEqual({row['original_annotation_id'] for row in key}, {'ann_0', 'ann_1'})
        self.assertEqual({row['model_key'] for row in key}, set(self.models))
        self.assertEqual(metadata['labels_completed'], 0)
        for row in queue:
            self.assertNotIn('model_key', row)
            self.assertNotIn('defense_condition', row)
            self.assertNotIn('case_id', row)
            self.assertTrue(row['annotation_id'].startswith('pool_'))
            self.assertEqual(row['gold_label'], '')

    def test_archive_integrity_is_required(self):
        wrong = dict(self.hashes)
        wrong[self.models[0]] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            build_package(self.paths, wrong, expected_cases=2)

    def test_incorrect_or_incomplete_model_inputs_rejected(self):
        with self.assertRaises(ValueError):
            build_package(self.paths, {self.models[0]: self.hashes[self.models[0]]},
                          expected_cases=2)
        with self.assertRaisesRegex(ValueError, 'run counts mismatch'):
            build_package(self.paths, self.hashes, expected_cases=3)

    def test_already_labeled_queue_is_rejected(self):
        self.hashes[self.models[0]] = fixture_archive(
            self.paths[self.models[0]], self.models[0], already_labeled=True)
        with self.assertRaisesRegex(ValueError, 'already labeled'):
            build_package(self.paths, self.hashes, expected_cases=2)

    def test_private_output_permissions_integrity_and_no_overwrite(self):
        queue, key, metadata = build_package(self.paths, self.hashes, expected_cases=2)
        out = Path(self.folder.name) / 'private'
        report = write_package(queue, key, metadata, out)
        csv_path = out / 'blinded_annotation_queue.csv'
        key_path = out / 'PRIVATE_annotation_crosswalk.jsonl'
        self.assertEqual(digest(csv_path.read_bytes()), report['blinded_queue_sha256'])
        self.assertEqual(digest(key_path.read_bytes()), report['private_crosswalk_sha256'])
        if os.name == 'posix':
            self.assertEqual(out.stat().st_mode & 0o777, 0o700)
            self.assertEqual(csv_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(key_path.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            write_package(queue, key, metadata, out)


if __name__ == '__main__':
    unittest.main()
