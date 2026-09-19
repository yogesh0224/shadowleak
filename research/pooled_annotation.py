"""Package frozen ShadowLeak model archives for pooled, blinded human annotation.

This is packaging only: model responses and frozen experimental inputs are not
changed. Keep the generated private crosswalk away from human annotators.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import zipfile

STUDY_ID = 'shadowleak-confirmatory-v1'
PLAN_SHA = 'ad9aadfa7b08de909795d1679ead723ae00333595440c1fda4b4d877d7ebe21e'
MODEL_REVISIONS = {
    'qwen2_5_1_5b_instruct': '989aa7980e4cf806f80c7fef2b1adb7bc71aa306',
    'qwen2_5_0_5b_instruct': '7ae557604adf67be50417f59c2c2f167def9a775',
    'smollm2_360m_instruct': 'a10cc1512eabd3dde888204e902eca88bddb4951',
    'tinyllama_1_1b_chat_v1': 'fe8a4ea1ffedaf415f4da2f062534de366a451e6',
}
ANON_FIELDS = ('annotation_id', 'task_type', 'prompt', 'synthetic_context',
               'target_field', 'protected_value', 'response', 'gold_label',
               'leak_type', 'utility_preserved', 'task_completion', 'correctness',
               'relevance', 'over_refusal', 'annotator_id', 'adjudication_status', 'rationale')
BLANK_FIELDS = ('gold_label', 'leak_type', 'utility_preserved', 'task_completion',
                'correctness', 'relevance', 'over_refusal', 'annotator_id',
                'adjudication_status', 'rationale')
SOURCE_FILES = ('run_summary.json', 'annotation_queue.csv', 'annotation_key.jsonl',
                'manifest.jsonl', 'responses.jsonl')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonlines(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode('utf-8').splitlines() if line.strip()]


def read_source(model_key: str, archive_path: Path, expected_sha: str,
                expected_cases: int = 1860) -> tuple[list[dict], list[dict], str]:
    archive_bytes = archive_path.read_bytes()
    observed_sha = digest(archive_bytes)
    if observed_sha != expected_sha.lower():
        raise ValueError(f'{model_key}: original ZIP SHA-256 differs from recorded evidence')
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        if archive.testzip() is not None:
            raise ValueError(f'{model_key}: ZIP integrity check failed')
        if not set(SOURCE_FILES).issubset(archive.namelist()):
            raise ValueError(f'{model_key}: required original files are missing')
        summary = json.loads(archive.read('run_summary.json'))
        if (summary['study_id'] != STUDY_ID or summary['study_plan_sha256'] != PLAN_SHA
            or summary['model']['key'] != model_key
            or summary['model']['revision'] != MODEL_REVISIONS[model_key]
            or summary['completed_cases'] != expected_cases or summary['failed_cases'] != 0
            or summary['planned_cases'] != expected_cases):
            raise ValueError(f'{model_key}: frozen study, model identity, or run counts mismatch')
        for name, recorded_sha in summary['artifacts'].items():
            if name not in archive.namelist() or digest(archive.read(name)) != recorded_sha:
                raise ValueError(f'{model_key}: internal artifact hash mismatch: {name}')
        rows = list(csv.DictReader(io.StringIO(archive.read('annotation_queue.csv').decode('utf-8'), newline='')))
        keys = jsonlines(archive.read('annotation_key.jsonl'))
        responses = jsonlines(archive.read('responses.jsonl'))
        manifest_sha = digest(archive.read('manifest.jsonl'))
    if len(rows) != len(keys) or len(rows) != len(responses) or len(rows) != expected_cases:
        raise ValueError(f'{model_key}: row counts do not match completed responses')
    if not rows or tuple(rows[0]) != ANON_FIELDS:
        raise ValueError(f'{model_key}: unexpected annotation queue columns')
    if any(any(str(row.get(field, '')).strip() for field in BLANK_FIELDS) for row in rows):
        raise ValueError(f'{model_key}: original annotation queue is already labeled')
    original_ids = [row['annotation_id'] for row in rows]
    if len(set(original_ids)) != len(original_ids):
        raise ValueError(f'{model_key}: duplicated original annotation ID within model')
    if len({item['annotation_id'] for item in keys}) != len(keys):
        raise ValueError(f'{model_key}: duplicate source key ID')
    key_by_id = {item['annotation_id']: item['case_id'] for item in keys}
    response_by_case = {item['case_id']: item for item in responses}
    if (set(original_ids) != set(key_by_id) or len(response_by_case) != len(responses)
        or set(key_by_id.values()) != set(response_by_case)):
        raise ValueError(f'{model_key}: original queue/key/response mapping incomplete')
    crosswalk = []
    for row in rows:
        case_id = key_by_id[row['annotation_id']]
        response = response_by_case[case_id]
        if (response.get('failed') or response.get('study_id') != STUDY_ID
            or response.get('model_revision') != MODEL_REVISIONS[model_key]
            or response['response'] != row['response'] or response['prompt'] != row['prompt']
            or response['context'] != row['synthetic_context']
            or response['protected_value'] != row['protected_value']
            or response['target_field'] != row['target_field']
            or response['task_type'] != row['task_type']):
            raise ValueError(f'{model_key}: response/annotation queue mismatch')
        crosswalk.append({
            'model_key': model_key, 'original_annotation_id': row['annotation_id'],
            'original_case_id': case_id, 'pair_id': response['pair_id'],
            'record_id': response['record_id'],
            'defense_condition': response['defense_condition'],
        })
    return rows, crosswalk, manifest_sha


def build_package(archives: dict[str, Path], expected_shas: dict[str, str],
                  expected_cases: int = 1860) -> tuple[list[dict], list[dict], dict]:
    if set(archives) != set(expected_shas) or not archives or not set(archives).issubset(MODEL_REVISIONS):
        raise ValueError('Archive keys and expected-digest keys must match registered model keys')
    queued, crosswalk, source_info, manifests = [], [], {}, set()
    unique_pooled = set()
    for model_key in sorted(archives):
        rows, keys, manifest_sha = read_source(model_key, archives[model_key],
                                               expected_shas[model_key], expected_cases)
        manifests.add(manifest_sha)
        source_info[model_key] = {'zip_sha256': expected_shas[model_key].lower(),
                                  'completed': len(rows), 'manifest_sha256': manifest_sha}
        for row, original in zip(rows, keys):
            pooled_id = 'pool_' + secrets.token_hex(20)
            if pooled_id in unique_pooled:
                raise ValueError('Unexpected anonymous ID collision')
            unique_pooled.add(pooled_id)
            queued.append({**row, 'annotation_id': pooled_id})
            crosswalk.append({'annotation_id': pooled_id, **original})
    if len(manifests) != 1:
        raise ValueError('Original manifest differs between registered model runs')
    secrets.SystemRandom().shuffle(queued)
    if len(queued) != len(crosswalk) or len(unique_pooled) != len(queued):
        raise ValueError('Pooled queue/crosswalk cardinality mismatch')
    return queued, crosswalk, {'study_id': STUDY_ID, 'records_per_model': expected_cases,
                               'responses': len(queued), 'source_archives': source_info,
                               'labels_completed': 0, 'human_annotation_status': 'not_started'}


def parse_assignments(entries: list[str]) -> dict[str, str]:
    result = {}
    for item in entries:
        key, sep, value = item.partition('=')
        if not sep or not key or not value or key in result:
            raise ValueError('Use unique MODEL_KEY=VALUE arguments')
        result[key] = value
    return result


def write_package(queued: list[dict], crosswalk: list[dict], manifest: dict,
                  output_dir: Path) -> dict:
    if output_dir.is_symlink():
        raise ValueError('Output directory must not be a symlink')
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(output_dir, 0o700)
    names = ('blinded_annotation_queue.csv', 'PRIVATE_annotation_crosswalk.jsonl',
             'PRIVATE_packaging_manifest.json')
    if any((output_dir / name).exists() for name in names):
        raise FileExistsError('Refusing to overwrite an existing annotation package')
    csv_buffer = io.StringIO(newline='')
    writer = csv.DictWriter(csv_buffer, fieldnames=ANON_FIELDS)
    writer.writeheader()
    writer.writerows(queued)
    queue_bytes = csv_buffer.getvalue().encode('utf-8')
    key_bytes = (''.join(json.dumps(row, sort_keys=True) + '\n' for row in crosswalk)).encode('utf-8')
    manifest = {**manifest, 'blinded_queue_sha256': digest(queue_bytes),
                'private_crosswalk_sha256': digest(key_bytes),
                'blinded_queue_columns': list(ANON_FIELDS),
                'key_must_be_separated_from_annotators': True}
    payloads = (queue_bytes, key_bytes, (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode())
    for name, payload in zip(names, payloads):
        fd = os.open(output_dir / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(payload)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', action='append', required=True, metavar='MODEL_KEY=ZIP_PATH')
    parser.add_argument('--sha256', action='append', required=True, metavar='MODEL_KEY=SHA256')
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    paths = {k: Path(v) for k, v in parse_assignments(args.archive).items()}
    expected = parse_assignments(args.sha256)
    if set(paths) != set(MODEL_REVISIONS) or set(expected) != set(paths):
        parser.error('Supply all four distinct registered model ZIPs and their audited SHA-256 values')
    if any(re.fullmatch('[0-9a-fA-F]{64}', value) is None for value in expected.values()):
        parser.error('Every SHA-256 must be exactly 64 hexadecimal characters')
    os.umask(0o077)
    queued, crosswalk, metadata = build_package(paths, expected)
    report = write_package(queued, crosswalk, metadata, args.output_dir)
    print(json.dumps({'status': 'PACKAGED_NOT_ANNOTATED',
                      'blinded_rows': report['responses'],
                      'distinct_pooled_ids': len({row['annotation_id'] for row in queued}),
                      'original_model_archives_verified': len(report['source_archives']),
                      'blinded_queue_sha256': report['blinded_queue_sha256'],
                      'private_crosswalk_sha256': report['private_crosswalk_sha256'],
                      'output_dir': str(args.output_dir)}, indent=2))


if __name__ == '__main__':
    main()
