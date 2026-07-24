#!/usr/bin/env python3
"""Rewrite Russian + Armenian UI and catalog localizations from English.

Tone: friendly / informal.
Armenian gym terms: natural (մոտեցում, կրկնություն).
Preserves keys, placeholders, and catalog IDs.

Requires: /tmp/wl-translate-venv with deep-translator
  /tmp/wl-translate-venv/bin/python scripts/rewrite_ru_hy.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "remote/translations/locales"
MANIFEST_PATH = ROOT / "remote/manifest.json"
CACHE_PATH = ROOT / "scripts/.ru_hy_rewrite_cache.json"

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[@difsca]|%\d+\$@|\{[^}]+\}|<[^>]+>")
SKIP_LITERAL_RE = re.compile(
    r"^(?:JSON|CSV(?: \(ZIP\))?|OK|e1RM(?: %@)?|Apple(?: Health)?|Google|Gym Logbook|"
    r"%[@dl]+(?: %@)?|%1\$[@dl]+ %2\$@|%lld|1|10:00|·|•|— × —|62\.5 × 8|"
    r"60 × 8 · 60 × 8 · 62\.5 × 6|"
    r"duration\.mode\.%@\.short|loggingType\.plain\.%@\.title|onboarding\.chapter\.%@\.title)$"
)

RU_GLOSSARY = [
    (r"\bсеты\b", "подходы"),
    (r"\bсетов\b", "подходов"),
    (r"\bсета\b", "подхода"),
    (r"\bсет\b", "подход"),
]

HY_GLOSSARY = [
    (r"սեթեր", "մոտեցումներ"),
    (r"սեթ(?!եր|ի|ում)", "մոտեցում"),
    (r"ռեփեր", "կրկնություններ"),
    (r"ռեփ(?!եր|ի)", "կրկնություն"),
    (r"վորքաութ", "մարզում"),
    (r"եքսերսայզ", "վարժություն"),
]

RU_OVERRIDES = {
    "common.done": "Готово",
    "common.cancel": "Отмена",
    "common.save": "Сохранить",
    "common.delete": "Удалить",
    "common.edit": "Изменить",
    "common.retry": "Повторить",
    "common.continue": "Продолжить",
    "common.close": "Закрыть",
    "common.search": "Поиск",
    "common.add": "Добавить",
    "tab.workout": "Тренировка",
    "tab.history": "История",
    "tab.templates": "Шаблоны",
    "tab.records": "Рекорды",
    "workout.startEmpty": "Начать пустую",
    "workout.startBalanced": "Сбалансированная",
    "workout.startBalanced.subtitle": "Выбери мышцы · подсказки по твоей статистике",
    "workout.noExercisesYet": "Пока нет упражнений. Добавь одно, чтобы писать подходы.",
    "set.deleteConfirmMessage": "В этом подходе уже есть значения. Точно удалить?",
    "rest.timer.needsSets": "Сначала добавь подход, потом запускай отдых.",
    "rest.timer.supersetUneven": "Закончи круг — у всех упражнений должно быть одинаковое число подходов.",
    "empty.records.description": "Рекорды появятся, когда побьёшь свой прошлый лучший результат.",
    "account.status.guestSubtitle": "Можно вести дневник уже сейчас. Войди, когда захочешь постоянный аккаунт.",
    "onboarding.ready.body": "Запиши первую тренировку — или просто поброди по вкладкам.",
    "onboarding.templates.body": "Собери шаблон один раз. При старте плановые подходы заполнятся сами — и тренировка пойдёт быстрее.",
    "onboarding.layout.body": "Список — для быстрого выбора, карточки — с картинками и мышцами.",
    "onboarding.insights.exportTip": "Бэкап в любой момент: Insights → Export (JSON или CSV).",
    "onboarding.balanced.where": "Вкладка «Тренировка» → «Сбалансированная»",
    "balanced.suggestions.replace.footerCards": "Нажми карточку, чтобы включить. Info — детали техники. Обновить — заменить упражнение.",
    "gate.forceUpdate.upcoming": "Что появится в этом обновлении",
    "gate.maintenance.title": "Скоро вернёмся",
    "gate.maintenance.message": "Gym Logbook на обслуживании. Загляни чуть позже.",
    "gate.forceUpdate.title": "Нужно обновление",
    "gate.forceUpdate.message": "Чтобы продолжить, установи более новую версию Gym Logbook.",
}

HY_OVERRIDES = {
    "common.done": "Պատրաստ է",
    "common.cancel": "Չեղարկել",
    "common.save": "Պահպանել",
    "common.delete": "Ջնջել",
    "common.edit": "Խմբագրել",
    "common.retry": "Կրկին փորձել",
    "common.continue": "Շարունակել",
    "common.close": "Փակել",
    "common.search": "Որոնել",
    "common.close": "Փակել",
    "common.search": "Որոնել",
    "common.add": "Ավելացնել",
    "tab.workout": "Մարզում",
    "tab.history": "Պատմություն",
    "tab.templates": "Կաղապարներ",
    "tab.records": "Ռեկորդներ",
    "workout.startEmpty": "Սկսել դատարկ",
    "workout.startBalanced": "Հավասարակշիռ",
    "workout.startBalanced.subtitle": "Ընտրիր մկաններ · առաջարկներ քո վիճակագրությունից",
    "workout.noExercisesYet": "Դեռ վարժություններ չկան։ Ավելացրու մեկը՝ մոտեցումներ գրանցելու համար։",
    "set.deleteConfirmMessage": "Այս մոտեցումն արդեն արժեքներ ունի։ Իսկապե՞ս ջնջել։",
    "rest.timer.needsSets": "Հանգիստը սկսելուց առաջ ավելացրու մոտեցում։",
    "rest.timer.supersetUneven": "Ավարտիր շրջափուլը — բոլոր վարժությունները պետք է ունենան նույն թվով մոտեցումներ։",
    "empty.records.description": "Ռեկորդները կհայտնվեն, երբ գերազանցես նախորդ լավագույն արդյունքը։",
    "account.status.guestSubtitle": "Կարող ես հիմա գրանցել մարզումներ։ Մուտք գործիր, երբ ցանկանաս մշտական հաշիվ։",
    "onboarding.ready.body": "Գրանցիր առաջին մարզումը — կամ հանգիստ ուսումնասիրիր ներդիրները։",
    "onboarding.templates.body": "Կառուցիր կաղապարը մեկ անգամ։ Սկսելիս պլանավորված մոտեցումները կլրացվեն իրենք — և մարզումն ավելի արագ կընթանա։",
    "onboarding.layout.body": "Ցանկը՝ արագ ընտրության համար, քարտերը՝ պատկերներով և մկանների հուշումներով։",
    "onboarding.insights.exportTip": "Պահուստավորիր ցանկացած պահի Insights → Export-ից (JSON կամ CSV)։",
    "onboarding.balanced.where": "«Մարզում» ներդիր → «Հավասարակշիռ»",
    "balanced.suggestions.replace.footerCards": "Հպիր քարտին՝ ներառելու համար։ Info՝ տեխնիկայի մանրամասներ։ Թարմացնել՝ վարժությունը փոխարինելու համար։",
    "gate.forceUpdate.upcoming": "Այս թարմացման մեջ",
    "gate.maintenance.title": "Շուտով կվերադառնանք",
    "gate.maintenance.message": "Gym Logbook-ը սպասարկման մեջ է։ Փորձիր մի փոքր ուշ։",
    "gate.forceUpdate.title": "Անհրաժեշտ է թարմացում",
    "gate.forceUpdate.message": "Շարունակելու համար տեղադրիր Gym Logbook-ի ավելի նոր տարբերակը։",
}



def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protect_placeholders(text: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def repl(match: re.Match[str]) -> str:
        tokens.append(match.group(0))
        return f"⟦PH{len(tokens) - 1}⟧"

    return PLACEHOLDER_RE.sub(repl, text), tokens


def restore_placeholders(text: str, tokens: list[str]) -> str:
    out = text
    for i, token in enumerate(tokens):
        for candidate in (f"⟦PH{i}⟧", f"[PH{i}]", f"(PH{i})", f"PH{i}"):
            if candidate in out:
                out = out.replace(candidate, token)
                break
    return out


def apply_glossary(text: str, pairs: list[tuple[str, str]]) -> str:
    out = text
    for pattern, repl in pairs:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def should_keep_literal(en: str) -> bool:
    if SKIP_LITERAL_RE.match(en.strip()):
        return True
    if en.strip() == "" or en.isspace():
        return True
    return False


def soften_ru(text: str) -> str:
    out = text
    replacements = [
        (r"\bВы\b", "ты"),
        (r"\bвам\b", "тебе"),
        (r"\bвас\b", "тебя"),
        (r"\bваш\b", "твой"),
        (r"\bваша\b", "твоя"),
        (r"\bваше\b", "твоё"),
        (r"\bваши\b", "твои"),
        (r"\bВаш\b", "Твой"),
        (r"\bВаша\b", "Твоя"),
        (r"\bВаше\b", "Твоё"),
        (r"\bВаши\b", "Твои"),
    ]
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out)
    return out


class Translator:
    def __init__(self) -> None:
        from deep_translator import GoogleTranslator

        self._GoogleTranslator = GoogleTranslator
        self.cache = load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
        self._lock = Lock()

    def get(self, text: str, locale: str) -> str | None:
        with self._lock:
            return self.cache.get(locale, {}).get(text)

    def put(self, text: str, locale: str, value: str) -> None:
        with self._lock:
            self.cache.setdefault(locale, {})[text] = value

    def save(self) -> None:
        dump_json(CACHE_PATH, self.cache)

    def translate(self, text: str, locale: str) -> str:
        self.ensure_translated([text], locale)
        if should_keep_literal(text):
            return text
        return self.get(text, locale) or text

    def ensure_translated(self, texts: list[str], locale: str) -> None:
        pending: list[str] = []
        seen: set[str] = set()
        for text in texts:
            if text in seen:
                continue
            seen.add(text)
            if should_keep_literal(text):
                continue
            if self.get(text, locale) is None:
                pending.append(text)
        if not pending:
            return

        target = "ru" if locale == "ru" else "hy"
        glossary = RU_GLOSSARY if locale == "ru" else HY_GLOSSARY
        batch_size = 25
        for i in range(0, len(pending), batch_size):
            chunk = pending[i : i + batch_size]
            protected_chunk = []
            token_lists: list[list[str]] = []
            for text in chunk:
                protected, tokens = protect_placeholders(text)
                protected_chunk.append(protected)
                token_lists.append(tokens)
            try:
                # deep-translator supports list input on some versions; fall back per-item.
                translator = self._GoogleTranslator(source="en", target=target)
                try:
                    translated_list = translator.translate_batch(protected_chunk)
                except Exception:
                    translated_list = [translator.translate(t) for t in protected_chunk]
            except Exception:
                translated_list = list(protected_chunk)

            for src, protected, tokens, translated in zip(
                chunk, protected_chunk, token_lists, translated_list
            ):
                out = restore_placeholders(translated or protected, tokens)
                out = apply_glossary(out, glossary)
                if locale == "ru":
                    out = soften_ru(out)
                self.put(src, locale, out)
            self.save()
            print(f"  translated {min(i+batch_size, len(pending))}/{len(pending)} [{locale}]")


def rewrite_ui(translator: Translator) -> None:
    keys: list[str] = load_json(LOCALES_DIR / "keys.json")
    en = load_json(LOCALES_DIR / "en.json")
    locales = {
        loc: load_json(LOCALES_DIR / f"{loc}.json")
        for loc in ("en", "ru", "hy", "sv", "nb", "nl", "da", "pl", "fr", "ar")
    }

    catalog_prefixes = ("exercise.catalog.", "superset.catalog.", "template.catalog.")
    work = [k for k in keys if not any(k.startswith(p) for p in catalog_prefixes)]
    print(f"Rewriting {len(work)} UI keys for ru/hy…")

    def one(key: str, locale: str) -> tuple[str, str, str]:
        src = en[key]
        overrides = RU_OVERRIDES if locale == "ru" else HY_OVERRIDES
        if key in overrides:
            return key, locale, overrides[key]
        if should_keep_literal(src):
            return key, locale, src
        return key, locale, translator.translate(src, locale)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(one, key, loc) for key in work for loc in ("ru", "hy")]
        done = 0
        for fut in as_completed(futures):
            key, locale, text = fut.result()
            locales[locale][key] = text
            done += 1
            if done % 200 == 0:
                translator.save()
                print(f"  UI progress {done}/{len(futures)}")

    catalog_keys = [k for k in keys if any(k.startswith(p) for p in catalog_prefixes)]
    print(f"Rewriting {len(catalog_keys)} legacy catalog keys…")
    for key in catalog_keys:
        src = en[key]
        for locale in ("ru", "hy"):
            overrides = RU_OVERRIDES if locale == "ru" else HY_OVERRIDES
            if key in overrides:
                locales[locale][key] = overrides[key]
            elif should_keep_literal(src):
                locales[locale][key] = src
            else:
                locales[locale][key] = translator.translate(src, locale)

    dump_json(LOCALES_DIR / "keys.json", keys)
    for loc, data in locales.items():
        ordered = {k: data[k] for k in keys if k in data}
        dump_json(LOCALES_DIR / f"{loc}.json", ordered)
    translator.save()
    print("UI locale files updated")


def rewrite_catalog_localizations(translator: Translator) -> None:
    manifest = load_json(MANIFEST_PATH)
    exercises_ptr = manifest["catalog"]["exercises"]
    supersets_ptr = manifest["catalog"]["supersets"]
    ex_version = int(exercises_ptr["version"])
    su_version = int(supersets_ptr["version"])

    en_ex_candidates = sorted(
        (ROOT / "remote/catalog/localizations/en").glob("v*/exercises.localization.json")
    )
    en_su_candidates = sorted(
        (ROOT / "remote/catalog/localizations/en").glob("v*/supersets.localization.json")
    )
    en_ex = load_json(en_ex_candidates[-1])
    en_su = load_json(en_su_candidates[-1])

    for locale in ("ru", "hy"):
        current_ex = int(manifest["catalog"]["localizations"][locale]["exercises"]["version"])
        current_su = int(manifest["catalog"]["localizations"][locale]["supersets"]["version"])
        new_ex_version = max(current_ex + 1, 4)
        new_su_version = current_su + 1
        print(
            f"Rewriting catalog localizations for {locale} → "
            f"exercises v{new_ex_version}, supersets v{new_su_version}"
        )

        # Prefetch all source strings for this locale in batches.
        corpus: list[str] = []
        for row in en_ex["exercises"].values():
            if row.get("name"):
                corpus.append(row["name"])
            for line in row.get("instructions") or []:
                corpus.append(line)
            for item in row.get("safety") or []:
                corpus.append(item["title"])
                corpus.append(item["description"])
        for row in en_su["supersets"].values():
            if row.get("name"):
                corpus.append(row["name"])
        print(f"  prefetch {len(corpus)} catalog strings for {locale}")
        translator.ensure_translated(corpus, locale)

        out_ex = {
            "schemaVersion": 1,
            "language": locale,
            "version": new_ex_version,
            "catalogVersion": ex_version,
            "exercises": {},
        }
        for eid, row in en_ex["exercises"].items():
            translated: dict = {}
            if row.get("name"):
                translated["name"] = translator.translate(row["name"], locale)
            if row.get("instructions"):
                translated["instructions"] = [
                    translator.translate(line, locale) for line in row["instructions"]
                ]
            if row.get("safety"):
                translated["safety"] = [
                    {
                        "index": item["index"],
                        "title": translator.translate(item["title"], locale),
                        "description": translator.translate(item["description"], locale),
                    }
                    for item in row["safety"]
                ]
            out_ex["exercises"][eid] = translated

        out_su = {
            "schemaVersion": 1,
            "language": locale,
            "version": new_su_version,
            "catalogVersion": su_version,
            "supersets": {},
        }
        for sid, row in en_su["supersets"].items():
            translated = {}
            if row.get("name"):
                translated["name"] = translator.translate(row["name"], locale)
            out_su["supersets"][sid] = translated

        ex_dir = ROOT / f"remote/catalog/localizations/{locale}/v{new_ex_version}"
        su_dir = ROOT / f"remote/catalog/localizations/{locale}/v{new_su_version}"
        dump_json(ex_dir / "exercises.localization.json", out_ex)
        dump_json(su_dir / "supersets.localization.json", out_su)

        raw = "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main"
        manifest["catalog"]["localizations"][locale]["exercises"] = {
            "version": new_ex_version,
            "url": f"{raw}/remote/catalog/localizations/{locale}/v{new_ex_version}/exercises.localization.json",
        }
        manifest["catalog"]["localizations"][locale]["supersets"] = {
            "version": new_su_version,
            "url": f"{raw}/remote/catalog/localizations/{locale}/v{new_su_version}/supersets.localization.json",
        }
        translator.save()

    manifest["maintenance"]["title"]["ru"] = "Скоро вернёмся"
    manifest["maintenance"]["title"]["hy"] = "Շուտով կվերադառնանք"
    manifest["maintenance"]["message"]["ru"] = "Gym Logbook на обслуживании. Загляни чуть позже."
    manifest["maintenance"]["message"]["hy"] = "Gym Logbook-ը սպասարկման մեջ է։ Փորձիր մի փոքր ուշ։"
    manifest["forceUpdate"]["title"]["ru"] = "Нужно обновление"
    manifest["forceUpdate"]["title"]["hy"] = "Անհրաժեշտ է թարմացում"
    manifest["forceUpdate"]["message"]["ru"] = (
        "Чтобы продолжить, установи более новую версию Gym Logbook."
    )
    manifest["forceUpdate"]["message"]["hy"] = (
        "Շարունակելու համար տեղադրիր Gym Logbook-ի ավելի նոր տարբերակը։"
    )

    if manifest.get("forceUpdate", {}).get("upcomingFeatures"):
        feature_updates = [
            {
                "en": "Faster workout logging",
                "ru": "Ещё быстрее записывать тренировки",
                "hy": "Ավելի արագ մարզման գրանցում",
            },
            {
                "en": "Richer muscle-balance insights",
                "ru": "Нагляднее видеть баланс мышц",
                "hy": "Ավելի հստակ մկանային հավասարակշռության վերլուծություն",
            },
            {
                "en": "Improved exercise catalog",
                "ru": "Удобнее каталог упражнений",
                "hy": "Ավելի հարմար վարժությունների կատալոգ",
            },
        ]
        old = manifest["forceUpdate"]["upcomingFeatures"]
        merged = []
        for i, feat in enumerate(feature_updates):
            base = dict(old[i]) if i < len(old) else {}
            base.update(feat)
            merged.append(base)
        manifest["forceUpdate"]["upcomingFeatures"] = merged

    dump_json(MANIFEST_PATH, manifest)
    print("Catalog localizations + manifest gate copy updated")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-only", action="store_true")
    parser.add_argument("--ui-only", action="store_true")
    args = parser.parse_args()

    translator = Translator()
    if not args.catalog_only:
        rewrite_ui(translator)
    if not args.ui_only:
        rewrite_catalog_localizations(translator)
    translator.save()
    subprocess.check_call(
        [sys.executable, str(ROOT / "scripts/compile_translations.py"), "--bump-timestamp"],
        cwd=str(ROOT),
    )
    print("Done")


if __name__ == "__main__":
    main()
