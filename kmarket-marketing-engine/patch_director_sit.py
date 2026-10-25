import sys
f = 'modules/drama_engine/drama_scenario_director.py'
txt = open(f, encoding='utf-8').read()

FIND = '\"personas\": dict(FIXED_PERSONAS),'
idx = txt.find(FIND)
if idx < 0:
    print('NOT_FOUND')
    sys.exit(1)

# 삽입 지점: personas 줄 끝 + \n        }\n        return payload
end_block = txt.find('\n        }\n        return payload', idx)
if end_block < 0:
    print('END_NOT_FOUND')
    sys.exit(1)

insert_at = end_block  # '\n        }\n...' 직전에 삽입
addition = '''
            # --- [2026-10-23 5컷판 cut0] 상황 자막 카드 텍스트 ---
            "situation_text": self._build_situation_text(
                genre=genre, location=location, speech_hook=speech_hook,
            ),'''

new_txt = txt[:insert_at] + addition + txt[insert_at:]

# _build_situation_text 정적 메서드 삽입 (return payload 바로 뒤)
AFTER = '        return payload\n\n    # ---------------------------------------------------------------- main'
if AFTER in new_txt:
    method_code = '''        return payload

    @staticmethod
    def _build_situation_text(genre, location, speech_hook):
        genre_name = (genre.get("name") or "").strip()
        loc_short  = location.split(" ")[0] if location else ""
        hook_prev  = speech_hook[:18] if speech_hook else ""
        lines = []
        if loc_short:  lines.append(loc_short)
        if genre_name: lines.append(genre_name)
        if hook_prev:  lines.append('"' + hook_prev + '..."')
        return "\\n".join(lines[:3]) if lines else "지금 이 순간,\\n무슨 일이 생겼냐면..."

    # ---------------------------------------------------------------- main'''
    new_txt = new_txt.replace(AFTER, method_code, 1)
    print('METHOD_INSERTED')
else:
    print('AFTER_NOT_FOUND')

open(f, 'w', encoding='utf-8').write(new_txt)
print('DONE')
