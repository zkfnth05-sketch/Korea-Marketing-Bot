# -*- coding: utf-8 -*-
"""
[Aura 전용 독립 모듈] AuraLinkSanitizer (brands/aura/aura_link_sanitizer.py)
=============================================================================
• 역할: 블로그/네이버 본문에 섞여 들어오는 '깨진 링크의 원천'을 제거
• 원인(실측): 네이버 블로그 유입 로그에서
    - `/](https:/aura-ai-dating.vercel.app/)`  ← [도메인](https://도메인) 마크다운이 자동링크로 깨짐
    - `/lounge\u00a0에\u00a0접속하여...`          ← 도메인/경로 뒤에 한글이 붙어 자동링크가 문장까지 삼킴
  기존 정제 정규식은 `http(s)://` 만 제거했기 때문에, 스킴 없는 도메인
  (`aura-ai-dating.vercel.app/lounge`)이 본문에 남아 네이버 에디터가 자동링크로 변환했음.
• 정책: 본문에는 어떤 형태의 URL/도메인도 남기지 않는다. (공식 링크는 별도 배너/댓글 모듈이 담당)
"""

import re

_MD_IMAGE = re.compile(r'!\[[^\]]*\]\([^)]*\)')
_MD_LINK = re.compile(r'\[([^\]]*)\]\(\s*[^)\s]*\s*\)')
_PAREN_URL = re.compile(r'\(\s*(?:https?://)?[A-Za-z0-9.-]+\.(?:vercel\.app|app|com|co\.kr|kr|net|io)[^\s)]*\s*\)')
_SCHEME_URL = re.compile(r'https?:/{1,2}[^\s\u00a0)\]]+')
_BARE_DOMAIN = re.compile(
    r'(?<![A-Za-z0-9@.-])(?:www\.)?[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*'
    r'\.(?:vercel\.app|app|com|co\.kr|kr|net|io|me)(?:/[^\s\u00a0)\]]*)?'
)
_LEFTOVER_MD = re.compile(r'\]\(\s*\)|\]\s*\(|\(\s*\)')


def sanitize_aura_body(text: str) -> str:
    """URL/도메인/마크다운 링크를 전부 제거한 순수 텍스트 반환 (NBSP 정규화 포함)."""
    if not text:
        return ""
    text = text.replace("\u00a0", " ")
    text = _MD_IMAGE.sub("", text)
    text = _MD_LINK.sub(lambda m: m.group(1) if not _BARE_DOMAIN.fullmatch(m.group(1).strip()) and not _SCHEME_URL.fullmatch(m.group(1).strip()) else "", text)
    text = _PAREN_URL.sub("", text)
    text = _SCHEME_URL.sub("", text)
    text = _BARE_DOMAIN.sub("", text)
    text = _LEFTOVER_MD.sub("", text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def has_link_residue(text: str) -> bool:
    """정제 후 본문에 링크 흔적이 남아있는지 검증 (봇 자체 무결성 게이트용)."""
    if not text:
        return False
    return bool(_SCHEME_URL.search(text) or _BARE_DOMAIN.search(text) or "](" in text)
