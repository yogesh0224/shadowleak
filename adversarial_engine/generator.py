import random
from core.models import GeneratedPrompt
from adversarial_engine.strategies import ATTACK_STRATEGIES
from adversarial_engine.mutator import mutate_prompt


CATEGORY_MAP = {
    "direct_extraction": "direct",
    "indirect_inference": "indirect",
    "roleplay_authority": "roleplay",
    "privacy_bypass": "obfuscated",
    "reconstruction": "obfuscated",
    "social_engineering": "roleplay",
}


def build_prompt_from_template(template: str, record):
    return template.format(
        name=record.name,
        email=record.email,
        phone=record.phone or "",
        city=record.city or "",
        organization=record.organization or "",
    )


def generate_adversarial_prompts_for_record(record, per_strategy=2):
    prompts = []

    for strategy_name, templates in ATTACK_STRATEGIES.items():
        sampled_templates = random.sample(templates, min(per_strategy, len(templates)))

        for template in sampled_templates:
            base_prompt = build_prompt_from_template(template, record)
            adversarial_prompt = mutate_prompt(base_prompt)

            prompt_obj, _ = GeneratedPrompt.objects.get_or_create(
                record=record,
                final_prompt=adversarial_prompt,
                defaults={
                    "template": None,
                    "category": CATEGORY_MAP.get(strategy_name, "obfuscated"),
                    "is_adversarial": True,
                    "attack_strategy": strategy_name,
                },
            )
            prompts.append(prompt_obj)

    return prompts