from core.models import PromptTemplate, GeneratedPrompt


def generate_prompts_for_record(record):
    prompts = []
    templates = PromptTemplate.objects.filter(active=True).order_by("id")

    for template in templates:
        try:
            final_prompt = template.template_text.format(
                name=record.name,
                email=record.email,
                phone=record.phone or "",
                city=record.city or "",
                organization=record.organization or "",
            )
        except Exception:
            continue

        prompt_obj, _ = GeneratedPrompt.objects.get_or_create(
            record=record,
            template=template,
            defaults={
                "final_prompt": final_prompt,
                "category": template.category,
            },
        )
        prompts.append(prompt_obj)

    return prompts
