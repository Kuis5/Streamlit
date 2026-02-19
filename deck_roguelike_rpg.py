import os
import sys

# Graphvizのパスを設定（最優先で実行）
if os.name == 'nt':  # Windows
    possible_paths = [
        r"C:\Program Files (x86)\Graphviz\bin",
        r"C:\Program Files\Graphviz\bin",
    ]
    for graphviz_path in possible_paths:
        if os.path.exists(graphviz_path):
            # PATHの先頭に追加（優先度を上げる）
            os.environ["PATH"] = graphviz_path + os.pathsep + os.environ["PATH"]
            break

import streamlit as st
import random
from typing import List, Optional
import game_data  # 永続データ管理
import styles as styles  # コンパクトなスタイル
import floor_tree  # フロアツリーシステム

# ===== 定数定義 =====

ELEMENT_NONE = "無"
ELEMENT_FIRE = "炎"
ELEMENT_WATER = "水"
ELEMENT_NATURE = "草"

CARD_ATTACK = "攻撃"
CARD_DEFEND = "防御"
CARD_BUFF = "バフ"
CARD_DEBUFF = "デバフ"
CARD_DRAW = "ドロー"

# ===== カードタイプとアイコン =====

CARD_TYPE_ICONS = {
    CARD_ATTACK: "⚔️",
    CARD_DEFEND: "🛡️",
    CARD_BUFF: "⭐",
    CARD_DEBUFF: "💀",
    CARD_DRAW: "🎴",
}

# デバフタイプのアイコン
DEBUFF_TYPE_ICONS = {
    "weaken": "⬇️",
    "stun": "💫",
    "poison": "☠️",
    "freeze": "❄️",
}

# ===== カードデータベース =====

def create_basic_cards() -> List[dict]:
    """基本カードセットを作成"""
    return [
        # 攻撃カード（高コストほどコスト効率良く）
        {"name": "基本攻撃", "type": CARD_ATTACK, "cost": 1, "element": ELEMENT_NONE, "damage": 10, "description": "ダメージ10"},
        {"name": "火球", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_FIRE, "damage": 22, "description": "ダメージ22 + 炎付与"},
        {"name": "水鉄砲", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_WATER, "damage": 22, "description": "ダメージ22 + 水付与"},
        {"name": "草の鞭", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_NATURE, "damage": 22, "description": "ダメージ22 + 草付与"},
        {"name": "メテオ", "type": CARD_ATTACK, "cost": 3, "element": ELEMENT_FIRE, "damage": 40, "description": "ダメージ40 + 炎付与"},
        {"name": "大洪水", "type": CARD_ATTACK, "cost": 3, "element": ELEMENT_WATER, "damage": 40, "description": "ダメージ40 + 水付与"},
        {"name": "森の怒り", "type": CARD_ATTACK, "cost": 3, "element": ELEMENT_NATURE, "damage": 40, "description": "ダメージ40 + 草付与"},
        {"name": "烈火斬", "type": CARD_ATTACK, "cost": 4, "element": ELEMENT_FIRE, "damage": 60, "description": "ダメージ60 + 炎付与"},
        
        # 防御カード（バランス調整）
        {"name": "基本防御", "type": CARD_DEFEND, "cost": 1, "element": ELEMENT_NONE, "shield": 8, "description": "シールド8獲得"},
        {"name": "鉄壁", "type": CARD_DEFEND, "cost": 2, "element": ELEMENT_NONE, "shield": 20, "description": "シールド20獲得"},
        {"name": "完全防御", "type": CARD_DEFEND, "cost": 3, "element": ELEMENT_NONE, "shield": 38, "description": "シールド38獲得"},
        
        # バフカード（効果を抑えて持続を長く）
        {"name": "闘志", "type": CARD_BUFF, "cost": 1, "element": ELEMENT_NONE, "buff_value": 0.15, "buff_duration": 2, "description": "攻撃力+15% 2ターン"},
        {"name": "集中", "type": CARD_BUFF, "cost": 2, "element": ELEMENT_NONE, "buff_value": 0.3, "buff_duration": 3, "description": "攻撃力+30% 3ターン"},
        {"name": "覚醒", "type": CARD_BUFF, "cost": 3, "element": ELEMENT_NONE, "buff_value": 0.6, "buff_duration": 2, "description": "攻撃力+60% 2ターン"},
        
        # ドローカード（コスト調整）
        {"name": "占い", "type": CARD_DRAW, "cost": 1, "element": ELEMENT_NONE, "draw_count": 1, "description": "カード1枚ドロー"},
        {"name": "策略", "type": CARD_DRAW, "cost": 2, "element": ELEMENT_NONE, "draw_count": 2, "description": "カード2枚ドロー"},
        {"name": "大量ドロー", "type": CARD_DRAW, "cost": 3, "element": ELEMENT_NONE, "draw_count": 3, "description": "カード3枚ドロー"},
        
        # デバフカード（敵を弱体化）
        {"name": "威圧", "type": CARD_DEBUFF, "cost": 1, "element": ELEMENT_NONE, "debuff_type": "weaken", "debuff_value": 0.25, "debuff_duration": 2, "description": "敵の攻撃力-25% 2ターン"},
        {"name": "束縛", "type": CARD_DEBUFF, "cost": 2, "element": ELEMENT_NONE, "debuff_type": "stun", "debuff_value": 1, "debuff_duration": 1, "description": "敵を1ターン行動不能にする"},
        {"name": "毒霧", "type": CARD_DEBUFF, "cost": 2, "element": ELEMENT_NATURE, "debuff_type": "poison", "debuff_value": 8, "debuff_duration": 4, "description": "毒: 4ターン間毎ターン8ダメージ + 草付与"},
        {"name": "呪縛", "type": CARD_DEBUFF, "cost": 3, "element": ELEMENT_NONE, "debuff_type": "weaken", "debuff_value": 0.5, "debuff_duration": 3, "description": "敵の攻撃力-50% 3ターン"},
        {"name": "氷結", "type": CARD_DEBUFF, "cost": 2, "element": ELEMENT_WATER, "debuff_type": "freeze", "debuff_value": 0.3, "debuff_duration": 2, "description": "敵の攻撃力-30% 2ターン + 水付与"},

        # 複合カード
        {"name": "連撃", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_NONE, "damage": 15, "draw_count": 1, "description": "ダメージ15 + カード1枚ドロー"},
        {"name": "防壁術", "type": CARD_DEFEND, "cost": 1, "element": ELEMENT_NONE, "shield": 12, "buff_value": 0.1, "buff_duration": 1, "description": "シールド12 + 攻撃+10% 1ターン"},
        {"name": "魔力強化", "type": CARD_BUFF, "cost": 2, "element": ELEMENT_NONE, "buff_value": 0.25, "buff_duration": 2, "draw_count": 1, "description": "攻撃+25% 2ターン + ドロー1枚"},
        {"name": "急速成長", "type": CARD_DRAW, "cost": 2, "element": ELEMENT_NATURE, "draw_count": 2, "damage": 10, "description": "カード2枚ドロー + ダメージ10"},
    ]

def create_starter_deck() -> List[dict]:
    """初期デッキを作成"""
    cards = []
    # 基本攻撃 × 3
    for _ in range(3):
        cards.append({"name": "基本攻撃", "type": CARD_ATTACK, "cost": 1, "element": ELEMENT_NONE, "damage": 10, "description": "ダメージ10"})
    # 元素攻撃カード（調整後の数値）
    cards.append({"name": "火球", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_FIRE, "damage": 22, "description": "ダメージ22 + 炎付与"})
    cards.append({"name": "水鉄砲", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_WATER, "damage": 22, "description": "ダメージ22 + 水付与"})
    cards.append({"name": "草の鞭", "type": CARD_ATTACK, "cost": 2, "element": ELEMENT_NATURE, "damage": 22, "description": "ダメージ22 + 草付与"})
    # 基本防御 × 2
    for _ in range(2):
        cards.append({"name": "基本防御", "type": CARD_DEFEND, "cost": 1, "element": ELEMENT_NONE, "shield": 8, "description": "シールド8獲得"})
    # 占い × 2
    for _ in range(2):
        cards.append({"name": "占い", "type": CARD_DRAW, "cost": 1, "element": ELEMENT_NONE, "draw_count": 1, "description": "カード1枚ドロー"})
    return cards

# ===== 元素反応システム =====

def check_element_reaction(current_element: Optional[str], new_element: str) -> tuple[bool, str, int, str]:
    """
    元素反応をチェック
    Returns: (反応発生, 反応名, 追加ダメージ, 反応タイプ)
    """
    if current_element is None or new_element == ELEMENT_NONE:
        return False, "", 0, ""
    
    reactions = {
        (ELEMENT_FIRE, ELEMENT_NATURE): ("🔥燃焼", 12, "持続ダメージ発動！", "burn"),
        (ELEMENT_NATURE, ELEMENT_FIRE): ("🔥燃焼", 12, "持続ダメージ発動！", "burn"),
        (ELEMENT_FIRE, ELEMENT_WATER): ("💧蒸発", 30, "大ダメージ！", "vaporize"),
        (ELEMENT_WATER, ELEMENT_FIRE): ("💧蒸発", 30, "大ダメージ！", "vaporize"),
        (ELEMENT_WATER, ELEMENT_NATURE): ("🌿成長", 25, "自然の力！", "bloom"),
        (ELEMENT_NATURE, ELEMENT_WATER): ("🌿成長", 25, "自然の力！", "bloom"),
    }
    
    reaction_key = (current_element, new_element)
    if reaction_key in reactions:
        name, damage, msg, reaction_type = reactions[reaction_key]
        return True, f"⚡元素反応 {name}！ {msg}", damage, reaction_type
    
    return False, "", 0, ""

# ===== ゲームロジック =====

def draw_cards(count: int):
    """カードをドローする"""
    for _ in range(count):
        if len(st.session_state.deck) == 0:
            # デッキが空なら捨て札をシャッフルして戻す
            if len(st.session_state.discard) == 0:
                break
            st.session_state.deck = st.session_state.discard.copy()
            st.session_state.discard = []
            random.shuffle(st.session_state.deck)
            st.session_state.battle_log.append("🔄 捨て札をシャッフルしてデッキに戻しました")
        
        if len(st.session_state.deck) > 0:
            card = st.session_state.deck.pop(0)
            st.session_state.hand.append(card)

def play_card(card_index: int):
    """カードをプレイする"""
    # インデックス範囲チェック（rerun後に手札が変わっている場合の防御）
    if card_index >= len(st.session_state.hand):
        return

    card = st.session_state.hand[card_index]
    cost = card.get("cost", 0)

    # エネルギー上限を強制（念のためクランプ）
    st.session_state.energy = min(st.session_state.energy, st.session_state.max_energy)

    # コストチェック（描画タイミングズレによる二重消費・不正使用を防ぐ）
    if st.session_state.energy < cost:
        st.session_state.battle_log.append(f"❌ エネルギー不足！（必要: {cost}, 残り: {st.session_state.energy}）")
        return

    # コスト消費
    st.session_state.energy -= cost
    # 念のため下限クランプ
    st.session_state.energy = max(0, st.session_state.energy)
    
    # エネルギー消費エフェクトを設定
    st.session_state.energy_effect = {
        "amount": cost
    }
    st.session_state.show_energy_effect = True
    
    st.session_state.battle_log.append(f"🎴 {card['name']} を使用！（コスト{cost}）")
    
    # カードの効果を適用
    card_type = card.get("type")
    
    if card_type == CARD_ATTACK:
        # ダメージ計算（バフ適用）
        base_damage = card.get("damage", 0)
        total_damage = base_damage
        if st.session_state.attack_buff_duration > 0:
            total_damage = int(total_damage * (1 + st.session_state.attack_buff))
            st.session_state.battle_log.append(f"💪 バフ効果で{base_damage} → {total_damage}ダメージに強化！")
        
        # 元素反応チェック
        reaction_occurred, reaction_msg, reaction_damage, reaction_type = check_element_reaction(
            st.session_state.enemy["element"], 
            card.get("element", ELEMENT_NONE)
        )
        
        reaction_bonus = 0
        if reaction_occurred:
            st.session_state.battle_log.append(reaction_msg)
            reaction_bonus = reaction_damage
            total_damage += reaction_damage
            
            # 燃焼反応の場合、持続ダメージを設定
            if reaction_type == "burn":
                st.session_state.enemy["burn"] = 10  # 毎ターン10ダメージ
                st.session_state.enemy["burn_duration"] = 3  # 3ターン持続
                st.session_state.battle_log.append(f"🔥 燃焼付与！ 3ターンの間、毎ターン10ダメージ")
            
            # 成長反応の場合、HP回復
            if reaction_type == "bloom":
                heal_amount = int(st.session_state.player_max_hp * 0.12)  # 最大HPの12%
                st.session_state.player_hp = min(st.session_state.player_max_hp, st.session_state.player_hp + heal_amount)
                st.session_state.battle_log.append(f"🌿 HP回復！ +{heal_amount} (現在: {st.session_state.player_hp}/{st.session_state.player_max_hp})")
            
            # 元素反応が起きたら元素をリセット＆クールダウン設定
            st.session_state.enemy["element"] = None
            st.session_state.enemy["element_duration"] = 0
            st.session_state.element_reaction_cooldown = 1  # 1ターン元素付着不可
        else:
            # 元素反応が起きなかった場合のみ新しい元素を付与
            element = card.get("element", ELEMENT_NONE)
            # クールダウン中は元素付着不可
            if element != ELEMENT_NONE and not hasattr(st.session_state, 'element_reaction_cooldown'):
                st.session_state.element_reaction_cooldown = 0
            
            if element != ELEMENT_NONE and st.session_state.element_reaction_cooldown == 0:
                st.session_state.enemy["element"] = element
                st.session_state.enemy["element_duration"] = 2
                st.session_state.battle_log.append(f"🔥 敵に{element}を付与！")
            elif element != ELEMENT_NONE and st.session_state.element_reaction_cooldown > 0:
                st.session_state.battle_log.append(f"⏳ 反応直後のため{element}は付着しなかった")
        
        # ダメージ適用（シールドを考慮）
        remaining_damage = total_damage
        shield_blocked = 0
        
        if st.session_state.enemy["shield"] > 0:
            if st.session_state.enemy["shield"] >= total_damage:
                # シールドで全て防げる
                shield_blocked = total_damage
                st.session_state.enemy["shield"] -= total_damage
                remaining_damage = 0
                st.session_state.battle_log.append(f"🛡️ 敵のシールドで{shield_blocked}ダメージを完全に防いだ！ (残りシールド: {st.session_state.enemy['shield']})")
            else:
                # シールドを貫通
                shield_blocked = st.session_state.enemy["shield"]
                remaining_damage = total_damage - st.session_state.enemy["shield"]
                st.session_state.battle_log.append(f"🛡️ 敵のシールドで{shield_blocked}ダメージを防いだ！ (残り{remaining_damage}ダメージ)")
                st.session_state.enemy["shield"] = 0
        
        # HPにダメージ
        st.session_state.enemy["hp"] -= remaining_damage
        if st.session_state.enemy["hp"] < 0:
            st.session_state.enemy["hp"] = 0
        
        # ダメージエフェクトを設定
        # 元素に応じた色を設定
        element = card.get("element", ELEMENT_NONE)
        element_colors = {
            ELEMENT_FIRE: "#ff4444",      # 炎: 赤
            ELEMENT_WATER: "#4488ff",     # 水: 青
            ELEMENT_NATURE: "#44ff44",    # 草: 緑
            ELEMENT_NONE: "#ff6b6b"       # 無: ピンク
        }
        effect_color = element_colors.get(element, "#ff6b6b")
        
        # 元素反応時は反応名を追加
        reaction_text = ""
        if reaction_occurred:
            # 反応名を抽出（"⚡元素反応 🔥燃焼！ 持続ダメージ発動！" から "🔥燃焼" を取得）
            reaction_name = reaction_msg.split("！")[0].split(" ")[-1] if "！" in reaction_msg else ""
            reaction_text = reaction_name
        
        st.session_state.damage_effect = {
            "type": "enemy",
            "amount": total_damage,
            "color": effect_color,
            "reaction": reaction_text
        }
        st.session_state.screen_shake = True
        st.session_state.show_effect = True  # エフェクト表示フラグをオン
        
        # 詳細なダメージログ
        if remaining_damage > 0:
            if reaction_bonus > 0:
                st.session_state.battle_log.append(f"⚔️ {remaining_damage}ダメージ！ (基本{base_damage} + 反応{reaction_bonus} - シールド{shield_blocked}) → 残りHP: {st.session_state.enemy['hp']}/{st.session_state.enemy['max_hp']}")
            else:
                st.session_state.battle_log.append(f"⚔️ {remaining_damage}ダメージ！ → 残りHP: {st.session_state.enemy['hp']}/{st.session_state.enemy['max_hp']}")
        elif shield_blocked > 0:
            # ダメージが0でもシールドでブロックした場合は表示済み
            pass

        # Bug2修正: 攻撃カードの複合ドロー効果（連撃など）
        if card.get("draw_count"):
            draw_count = card.get("draw_count", 0)
            draw_cards(draw_count)
            st.session_state.battle_log.append(f"📥 {draw_count}枚追加ドロー！（手札: {len(st.session_state.hand)}枚）")
    
    elif card_type == CARD_DEFEND:
        shield_amount = card.get("shield", 0)
        st.session_state.shield += shield_amount
        st.session_state.battle_log.append(f"🛡️ シールド{shield_amount}獲得！（現在: {st.session_state.shield}）")
        # 複合効果：防御+バフ（防壁術など）
        if card.get("buff_value"):
            new_buff = card.get("buff_value", 0)
            new_dur = card.get("buff_duration", 1)
            # バフは加算（上書きではなく最大値を採用し残りターンも延長）
            st.session_state.attack_buff = max(st.session_state.attack_buff, new_buff)
            st.session_state.attack_buff_duration = max(st.session_state.attack_buff_duration, new_dur)
            st.session_state.battle_log.append(f"💪 さらに攻撃力+{int(new_buff*100)}% {new_dur}ターン！")

    elif card_type == CARD_BUFF:
        new_buff = card.get("buff_value", 0)
        new_dur = card.get("buff_duration", 0)
        # バフは加算（既存バフより強ければ上書き、残りターンも延長）
        st.session_state.attack_buff = max(st.session_state.attack_buff, new_buff)
        st.session_state.attack_buff_duration = max(st.session_state.attack_buff_duration, new_dur)
        st.session_state.battle_log.append(f"💪 攻撃力+{int(new_buff*100)}% {new_dur}ターン！（現在: +{int(st.session_state.attack_buff*100)}%）")
        # 複合効果：バフ+ドロー（魔力強化など）
        if card.get("draw_count"):
            draw_count = card.get("draw_count", 0)
            draw_cards(draw_count)
            st.session_state.battle_log.append(f"📥 カード{draw_count}枚追加ドロー！（手札: {len(st.session_state.hand)}枚）")

    elif card_type == CARD_DEBUFF:
        debuff_type = card.get("debuff_type", "")
        debuff_value = card.get("debuff_value", 0)
        debuff_duration = card.get("debuff_duration", 1)

        if debuff_type == "weaken":
            # 弱体化: 敵の攻撃力を一時的に下げる
            if "debuff_weaken" not in st.session_state.enemy:
                st.session_state.enemy["debuff_weaken"] = 0
                st.session_state.enemy["debuff_weaken_duration"] = 0
            # 既存より強い弱体化のみ適用
            st.session_state.enemy["debuff_weaken"] = max(st.session_state.enemy.get("debuff_weaken", 0), debuff_value)
            st.session_state.enemy["debuff_weaken_duration"] = max(
                st.session_state.enemy.get("debuff_weaken_duration", 0), debuff_duration
            )
            st.session_state.battle_log.append(
                f"💀 敵に弱体化付与！ 攻撃力-{int(debuff_value*100)}% {debuff_duration}ターン"
            )
        elif debuff_type == "stun":
            # スタン: 次のターン行動不能
            st.session_state.enemy["stunned"] = True
            st.session_state.battle_log.append("💀 敵をスタン！ 次のターン行動不能")
        elif debuff_type == "poison":
            # 毒: 毎ターンダメージ（燃焼とは別管理）
            st.session_state.enemy["poison"] = debuff_value
            st.session_state.enemy["poison_duration"] = debuff_duration
            st.session_state.battle_log.append(
                f"☠️ 毒付与！ {debuff_duration}ターン間毎ターン{debuff_value}ダメージ"
            )
            # 草属性付与
            element = card.get("element", ELEMENT_NONE)
            if element != ELEMENT_NONE and st.session_state.element_reaction_cooldown == 0:
                st.session_state.enemy["element"] = element
                st.session_state.enemy["element_duration"] = 2
                st.session_state.battle_log.append(f"🌿 敵に草を付与！")
        elif debuff_type == "freeze":
            # 氷結: 攻撃力低下 + 水属性付与
            st.session_state.enemy["debuff_weaken"] = max(st.session_state.enemy.get("debuff_weaken", 0), debuff_value)
            st.session_state.enemy["debuff_weaken_duration"] = max(
                st.session_state.enemy.get("debuff_weaken_duration", 0), debuff_duration
            )
            st.session_state.battle_log.append(
                f"❄️ 氷結付与！ 攻撃力-{int(debuff_value*100)}% {debuff_duration}ターン"
            )
            element = card.get("element", ELEMENT_NONE)
            if element != ELEMENT_NONE and st.session_state.element_reaction_cooldown == 0:
                st.session_state.enemy["element"] = element
                st.session_state.enemy["element_duration"] = 2
                st.session_state.battle_log.append(f"💧 敵に水を付与！")

    elif card_type == CARD_DRAW:
        draw_count = card.get("draw_count", 0)
        draw_cards(draw_count)
        st.session_state.battle_log.append(f"📥 カード{draw_count}枚ドロー！（手札: {len(st.session_state.hand)}枚）")
        # Bug3修正: ドローカードの複合ダメージ効果（急速成長など）
        if card.get("damage"):
            base_damage = card.get("damage", 0)
            total_damage = base_damage
            if st.session_state.attack_buff_duration > 0:
                total_damage = int(total_damage * (1 + st.session_state.attack_buff))
            element = card.get("element", ELEMENT_NONE)
            reaction_occurred, reaction_msg, reaction_damage, reaction_type = check_element_reaction(
                st.session_state.enemy["element"], element
            )
            if reaction_occurred:
                st.session_state.battle_log.append(reaction_msg)
                total_damage += reaction_damage
                st.session_state.enemy["element"] = None
                st.session_state.enemy["element_duration"] = 0
                st.session_state.element_reaction_cooldown = 1
            elif element != ELEMENT_NONE and st.session_state.element_reaction_cooldown == 0:
                st.session_state.enemy["element"] = element
                st.session_state.enemy["element_duration"] = 2
            # ダメージ適用
            remaining = total_damage
            if st.session_state.enemy["shield"] > 0:
                blocked = min(st.session_state.enemy["shield"], total_damage)
                st.session_state.enemy["shield"] -= blocked
                remaining = total_damage - blocked
            st.session_state.enemy["hp"] = max(0, st.session_state.enemy["hp"] - remaining)
            if remaining > 0:
                st.session_state.battle_log.append(
                    f"⚔️ {remaining}ダメージ！ → 残りHP: {st.session_state.enemy['hp']}/{st.session_state.enemy['max_hp']}"
                )
    
    # カードを捨て札へ
    st.session_state.hand.pop(card_index)
    st.session_state.discard.append(card)

def enemy_turn():
    """敵のターン"""
    st.session_state.battle_log.append("--- 👾 敵のターン ---")

    # 毒ダメージ処理
    if st.session_state.enemy.get("poison_duration", 0) > 0:
        poison_dmg = st.session_state.enemy.get("poison", 0)
        st.session_state.enemy["hp"] -= poison_dmg
        if st.session_state.enemy["hp"] < 0:
            st.session_state.enemy["hp"] = 0
        st.session_state.battle_log.append(
            f"☠️ 毒ダメージ！ {poison_dmg}ダメージ (残り{st.session_state.enemy['poison_duration']}ターン)"
        )
        st.session_state.enemy["poison_duration"] -= 1
        if st.session_state.enemy["hp"] <= 0:
            st.session_state.shield = 0
            return

    # 敵が生きている場合のみ行動
    if st.session_state.enemy["hp"] > 0:
        # スタン中は行動スキップ
        if st.session_state.enemy.get("stunned", False):
            st.session_state.battle_log.append("💫 敵はスタン中！ 行動できない")
            st.session_state.enemy["stunned"] = False
        else:
            action = st.session_state.enemy["next_action"]
            desc, icon = get_action_description(action)

            # 弱体化による攻撃力補正
            base_attack = st.session_state.enemy["attack"]
            weaken = st.session_state.enemy.get("debuff_weaken", 0)
            effective_attack = int(base_attack * (1 - weaken))

            if action == "attack":
                damage = effective_attack
                st.session_state.battle_log.append(f"{icon} 敵の{desc}！")
                if weaken > 0:
                    st.session_state.battle_log.append(f"⬇️ 弱体化中 (-{int(weaken*100)}%): {base_attack} → {effective_attack}")
                apply_damage_to_player(damage)

            elif action == "big_attack":
                damage = int(effective_attack * 1.5)
                st.session_state.battle_log.append(f"{icon} 敵の{desc}！")
                if weaken > 0:
                    st.session_state.battle_log.append(f"⬇️ 弱体化中 (-{int(weaken*100)}%): {int(base_attack*1.5)} → {damage}")
                apply_damage_to_player(damage)

            elif action == "defend":
                shield_amount = int(effective_attack * 1.2)
                st.session_state.enemy["shield"] += shield_amount
                st.session_state.battle_log.append(
                    f"{icon} 敵は{desc}を取った！ シールド+{shield_amount} (現在: {st.session_state.enemy['shield']})"
                )

        # 弱体化のターン経過
        if st.session_state.enemy.get("debuff_weaken_duration", 0) > 0:
            st.session_state.enemy["debuff_weaken_duration"] -= 1
            if st.session_state.enemy["debuff_weaken_duration"] == 0:
                st.session_state.enemy["debuff_weaken"] = 0
                st.session_state.battle_log.append("✅ 敵の弱体化が解除された")

        # 次の行動を決定
        decide_enemy_action()

    # プレイヤーのシールドをリセット
    st.session_state.shield = 0

def apply_damage_to_player(damage: int):
    """プレイヤーにダメージを適用"""
    # シールドで軽減
    if st.session_state.shield > 0:
        if st.session_state.shield >= damage:
            st.session_state.shield -= damage
            st.session_state.battle_log.append(f"🛡️ シールドで{damage}ダメージを完全に防いだ！ (残りシールド: {st.session_state.shield})")
            damage = 0
        else:
            damage -= st.session_state.shield
            st.session_state.battle_log.append(f"🛡️ シールドで{st.session_state.shield}ダメージを防いだ！ (残り{damage}ダメージ)")
            st.session_state.shield = 0
    
    # HPにダメージ
    if damage > 0:
        st.session_state.player_hp -= damage
        st.session_state.battle_log.append(f"💔 {damage}ダメージを受けた！ (残りHP: {st.session_state.player_hp}/{st.session_state.player_max_hp})")
        
        # プレイヤーダメージエフェクトを設定
        st.session_state.damage_effect = {
            "type": "player",
            "amount": damage,
            "color": "#ff4444",
            "reaction": ""  # プレイヤーダメージには反応なし
        }
        st.session_state.screen_shake = True
        st.session_state.screen_flash = "damage"
        st.session_state.show_effect = True  # エフェクト表示フラグをオン

def start_turn():
    """ターン開始処理"""
    # 燃焼ダメージ処理（ターン開始時）
    if st.session_state.enemy["burn_duration"] > 0:
        burn_damage = st.session_state.enemy["burn"]
        st.session_state.enemy["hp"] -= burn_damage
        if st.session_state.enemy["hp"] < 0:
            st.session_state.enemy["hp"] = 0
        st.session_state.battle_log.append(f"🔥 燃焼ダメージ！ {burn_damage}ダメージ (残り{st.session_state.enemy['burn_duration']}ターン)")

        # 燃焼ダメージエフェクトを表示
        st.session_state.damage_effect = {
            "type": "enemy",
            "amount": burn_damage,
            "color": "#ff4444",
            "reaction": "🔥燃焼"
        }
        st.session_state.show_effect = True

        st.session_state.enemy["burn_duration"] -= 1

    # エネルギー回復
    st.session_state.energy = st.session_state.max_energy

    # バフ期間減少（999=休憩所バフ=戦闘中ずっと有効→減らさない）
    if 0 < st.session_state.attack_buff_duration < 999:
        st.session_state.attack_buff_duration -= 1
        if st.session_state.attack_buff_duration == 0:
            st.session_state.attack_buff = 0

    # 元素期間減少（敵ごと、敵オブジェクト内で管理）
    if st.session_state.enemy.get("element_duration", 0) > 0:
        st.session_state.enemy["element_duration"] -= 1
        if st.session_state.enemy["element_duration"] == 0:
            st.session_state.enemy["element"] = None

    # 元素反応クールダウン減少
    if hasattr(st.session_state, 'element_reaction_cooldown') and st.session_state.element_reaction_cooldown > 0:
        st.session_state.element_reaction_cooldown -= 1

    # アップグレードによるドロー枚数ボーナスを適用
    draw_bonus = 0
    if hasattr(st.session_state, 'persistent_data'):
        draw_bonus = game_data.get_total_effect(st.session_state.persistent_data, "card_draw_bonus")
    draw_cards(5 + draw_bonus)

# ===== エネルギー表示関数 =====

def render_energy_bars(current_energy: int, max_energy: int) -> str:
    """
    エネルギーをmax_energy個のバーで表示
    各バーには⚡マークを表示
    """
    # 安全クランプ
    max_energy = max(1, int(max_energy))
    current_energy = max(0, min(int(current_energy), max_energy))

    html = f'<div style="width: 100%; margin-top: 4px; padding: 2px 0;">'
    html += f'<div style="font-size:0.7rem; color:rgba(255,255,255,0.7); margin-bottom:2px;">⚡ {current_energy}/{max_energy}</div>'
    html += '<div style="display: flex; gap: 3px; align-items: center;">'

    # max_energy個のバーを描画（最大10個まで）
    for i in range(min(max_energy, 10)):
        # バーi（0-4）が現在のエネルギー値より小さい場合は色、大きい場合は黒
        if i < current_energy:
            # 色（残りエネルギー）- グラデーション効果
            bg_gradient = "linear-gradient(135deg, #5DBDAE 0%, #6ECDC4 100%)"
            border_color = "rgba(110, 205, 196, 0.8)"
            box_shadow = "0 4px 12px rgba(110, 205, 196, 0.5), inset -1px -1px 3px rgba(0, 0, 0, 0.2)"
            icon = "⚡"
            icon_color = "#FFE135"
        else:
            # 黒（使用済み）- グラデーション効果
            bg_gradient = "linear-gradient(135deg, #252525 0%, #2C2C2C 100%)"
            border_color = "rgba(255, 255, 255, 0.2)"
            box_shadow = "0 2px 6px rgba(0, 0, 0, 0.4), inset 1px 1px 2px rgba(255, 255, 255, 0.05)"
            icon = ""
            icon_color = "transparent"
        
        bar_html = f"""<div style="
            flex: 1;
            height: 24px;
            background: {bg_gradient};
            border-radius: 4px;
            border: 1.5px solid {border_color};
            box-shadow: {box_shadow};
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: bold;
            color: {icon_color};
            cursor: default;
        ">{icon}</div>"""
        html += bar_html
    
    html += '</div>'
    html += '</div>'  # 外側div閉じる
    
    return html

# ===== UI表示 =====

def get_element_emoji(element: str) -> str:
    """元素の絵文字を取得"""
    emoji_map = {
        ELEMENT_FIRE: "🔥",
        ELEMENT_WATER: "💧",
        ELEMENT_NATURE: "🌿",
        ELEMENT_NONE: "⚪"
    }
    return emoji_map.get(element, "⚪")

def get_enemy_emoji(enemy_name: str) -> str:
    """敵の種族に応じた絵文字を取得"""
    emoji_map = {
        "スライム": "🟢",
        "ゴブリン": "👺",
        "オーク": "🐗",
        "ドラゴン": "🐉",
        "魔法使い": "🧙‍♂️",
    }
    return emoji_map.get(enemy_name, "👾")

def decide_enemy_action():
    """敵の次の行動を決定（改善版：より戦略的）"""
    import random
    
    hp_ratio = st.session_state.enemy["hp"] / st.session_state.enemy["max_hp"]
    shield = st.session_state.enemy["shield"]
    player_buff = st.session_state.attack_buff_duration > 0
    player_hp_ratio = st.session_state.player_hp / st.session_state.player_max_hp
    
    # 戦略的な行動決定
    if hp_ratio < 0.25:
        # 瀕死時：防御優先で生き延びる
        actions = ["defend"] * 6 + ["big_attack"] * 2 + ["attack"] * 2
    elif hp_ratio < 0.5:
        # 低HP時：防御/攻撃バランス + シールドがない場合は防御
        if shield < 10:
            actions = ["defend"] * 5 + ["big_attack"] * 3 + ["attack"] * 2
        else:
            actions = ["big_attack"] * 4 + ["attack"] * 4 + ["defend"] * 2
    elif hp_ratio < 0.75:
        # 中程度HP：バランスの取れた攻撃
        if player_buff:
            # プレイヤーがバフ状態なら防御
            actions = ["defend"] * 4 + ["big_attack"] * 4 + ["attack"] * 2
        else:
            actions = ["big_attack"] * 4 + ["attack"] * 5 + ["defend"] * 1
    else:
        # 高HP時：攻撃的
        if player_hp_ratio > 0.7:
            # プレイヤーHP多い→大攻撃で圧力
            actions = ["big_attack"] * 5 + ["attack"] * 4 + ["defend"] * 1
        else:
            # プレイヤーHP少ない→強気で攻撃
            actions = ["big_attack"] * 6 + ["attack"] * 3 + ["defend"] * 1
    
    st.session_state.enemy["next_action"] = random.choice(actions)

def create_enemy_data(name: str, difficulty: int) -> dict:
    """敵データを作成（改善版：10%削弱）"""
    # ゲームバランス調整：敵を約10%削弱
    hp_base = (45 + difficulty * 12) * 0.9  # 10%削弱
    attack_base = (6 + difficulty * 1.2) * 0.9  # 10%削弱
    
    return {
        "name": name,
        "max_hp": int(hp_base),
        "hp": int(hp_base),
        "attack": int(attack_base),
        "shield": 0,
        "element": None,
        "element_duration": 0,
        "burn": 0,
        "burn_duration": 0,
        "next_action": "attack",
        # デバフフィールド
        "debuff_weaken": 0,
        "debuff_weaken_duration": 0,
        "stunned": False,
        "poison": 0,
        "poison_duration": 0,
    }


def setup_battle_from_node(node):
    """ツリーのノードから戦闘をセットアップ"""
    if node.node_type != "battle":
        return  # 戦闘ノード以外はスキップ

    # 敵データを構造化して保存
    st.session_state.enemy = create_enemy_data(node.enemy_name, node.difficulty)

    # 敵の次の行動を決定
    decide_enemy_action()

    # プレイヤー状態をリセット（前の戦闘の残りをクリア）
    st.session_state.shield = 0
    st.session_state.element_reaction_cooldown = 0

    # 休憩所バフ（次の1戦限り）の引き継ぎ
    rest_buff = st.session_state.get('rest_attack_buff', 0)
    if rest_buff > 0:
        # 次の戦闘に持ち込む（戦闘中は全ターン有効: duration=999）
        st.session_state.attack_buff = rest_buff
        st.session_state.attack_buff_duration = 999  # 戦闘終了まで有効
        st.session_state.rest_attack_buff = 0  # 使い切り
    else:
        st.session_state.attack_buff = 0
        st.session_state.attack_buff_duration = 0

    # デッキをリセット
    st.session_state.deck = st.session_state.all_cards.copy()
    st.session_state.hand = []
    st.session_state.discard = []
    random.shuffle(st.session_state.deck)

    # ターン進行 & 現在階層を正しく設定
    st.session_state.turn += 1
    st.session_state.current_floor = node.floor_level
    st.session_state.energy = st.session_state.max_energy

    # アップグレードによるドロー枚数ボーナスを適用
    draw_bonus = 0
    if hasattr(st.session_state, 'persistent_data'):
        draw_bonus = game_data.get_total_effect(st.session_state.persistent_data, "card_draw_bonus")
    draw_cards(5 + draw_bonus)

    st.session_state.battle_log = [f"⚔️ 第{st.session_state.turn}戦: {st.session_state.enemy['name']}との戦闘開始！"]
    st.session_state.current_turn_log = []


def proceed_to_next_floor():
    """次の階層を選択する画面へ進む"""
    nodes = st.session_state.floor_nodes
    current_node_id = st.session_state.current_node_id
    current_node = nodes[current_node_id]

    # Bug4修正: 報酬関連の状態を確実にリセット
    st.session_state.reward_choice = None
    st.session_state.cards_to_delete = []
    if 'reward_cards_cache' in st.session_state:
        del st.session_state.reward_cards_cache

    left_child, right_child = floor_tree.get_node_children(nodes, current_node_id)

    # 子ノードが1つもない場合（ゲーム終了）
    if not left_child and not right_child:
        if current_node.floor_level == 10:
            st.session_state.game_state = 'clear'
        else:
            st.session_state.game_state = 'victory'
        return

    # それ以外の場合は常にマップ選択画面を表示
    st.session_state.game_state = 'tree_selection'
    return

def get_action_description(action: str) -> tuple[str, str]:
    """行動の説明とアイコンを取得"""
    descriptions = {
        "attack": ("通常攻撃", "⚔️"),
        "big_attack": ("強攻撃 (1.5倍)", "💥"),
        "defend": ("防御態勢 (ダメージ半減)", "🛡️"),
    }
    return descriptions.get(action, ("不明", "❓"))

def display_card(card: dict, key_prefix: str, index: int):
    """カードを表示する（ボタンは別で作成）- TCGスタイル"""
    # カードの色
    color_map = {
        ELEMENT_NONE: "#888888",
        ELEMENT_FIRE: "#FF6B6B",
        ELEMENT_WATER: "#4ECDC4",
        ELEMENT_NATURE: "#95E77D",
    }
    
    element = card.get("element", ELEMENT_NONE)
    card_type = card.get("type", CARD_ATTACK)
    color = color_map.get(element, "#888888")
    element_emoji = get_element_emoji(element)
    type_icon = CARD_TYPE_ICONS.get(card_type, "🎴")
    name = card.get('name', '')
    cost = card.get('cost', 0)
    description = card.get('description', '')
    
    # コスト判定
    can_use = st.session_state.energy >= cost
    
    # カードのスタイル
    if can_use:
        opacity_style = "opacity: 1;"
        border_style = "border: 4px solid rgba(255, 255, 255, 0.3);"
    else:
        opacity_style = "opacity: 0.5;"
        border_style = "border: 4px solid rgba(255, 0, 0, 0.5);"
    
    # TCGスタイルのカード（上部イラスト、中部情報、下部説明）
    card_html = f"""
<div style="background: linear-gradient(135deg, {color} 0%, {color}CC 100%); 
            {border_style}
            border-radius: 12px; 
            padding: 0; 
            margin: 8px 0; 
            color: white; 
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); 
            overflow: hidden;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
            {opacity_style}
            display: flex;
            flex-direction: column;">
    <div style="background: linear-gradient(135deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 100%); 
                padding: 20px 15px;
                text-align: center;
                border-bottom: 2px solid rgba(255,255,255,0.2);">
        <div style="font-size: 56px; font-weight: bold; line-height: 1;">
            {type_icon}
        </div>
    </div>
    <div style="padding: 12px 15px; background: rgba(0, 0, 0, 0.1);">
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
            <span>{element_emoji} {name}</span>
            <span style="background: rgba(0, 0, 0, 0.4); padding: 3px 8px; border-radius: 4px; font-size: 14px;">⚡{cost}</span>
        </div>
        <div style="font-size: 12px; color: rgba(255, 255, 255, 0.9); font-style: italic;">
            {card_type}
        </div>
    </div>
    <div style="padding: 10px 15px; background: rgba(0, 0, 0, 0.2); border-top: 1px solid rgba(255,255,255,0.2); font-size: 13px; line-height: 1.4;">
        {description}
    </div>
</div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # ボタンを返す
    return st.button(
        "✨ 使う" if can_use else "❌ コスト不足",
        key=f"use_{key_prefix}_{index}",
        disabled=not can_use,
        use_container_width=True,
        type="primary" if can_use else "secondary"
    )

def display_card_compact(card: dict, key_prefix: str, index: int):
    """コンパクトなカード表示（1画面表示用）- TCGスタイル"""
    color_map = {
        ELEMENT_NONE: "#888888",
        ELEMENT_FIRE: "#FF6B6B",
        ELEMENT_WATER: "#4ECDC4",
        ELEMENT_NATURE: "#95E77D",
    }
    
    element = card.get("element", ELEMENT_NONE)
    card_type = card.get("type", CARD_ATTACK)
    color = color_map.get(element, "#888888")
    element_emoji = get_element_emoji(element)
    type_icon = CARD_TYPE_ICONS.get(card_type, "🎴")
    name = card.get('name', '')
    cost = card.get('cost', 0)
    description = card.get('description', '')
    
    can_use = st.session_state.energy >= cost
    
    # コンパクトなカードHTML
    opacity = "1" if can_use else "0.5"
    border_color = "rgba(255, 255, 255, 0.3)" if can_use else "rgba(255, 0, 0, 0.5)"
    
    card_html = f"""
<div style="background: linear-gradient(135deg, {color} 0%, {color}CC 100%); 
            border: 2px solid {border_color};
            border-radius: 8px; 
            padding: 0; 
            margin: 2px 0; 
            color: white; 
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7); 
            min-height: 130px; 
            max-height: 130px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            opacity: {opacity};
            font-size: 0.75rem;
            overflow: hidden;
            display: flex;
            flex-direction: column;">
    <div style="background: rgba(0,0,0,0.2); padding: 6px; text-align: center; flex-shrink: 0;">
        <div style="font-size: 28px; line-height: 1;">{type_icon}</div>
    </div>
    <div style="padding: 4px 8px; background: rgba(0,0,0,0.1); flex-shrink: 0;">
        <div style="font-size: 0.8rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            {element_emoji} {name}
        </div>
        <div style="font-size: 0.65rem; background: rgba(0, 0, 0, 0.3); display: inline-block; padding: 1px 4px; border-radius: 3px; margin-top: 2px;">
            ⚡{cost}
        </div>
    </div>
    <div style="padding: 3px 8px; background: rgba(0,0,0,0.2); font-size: 0.65rem; line-height: 1.3; overflow: hidden; max-height: 3.5em; flex-grow: 1; word-wrap: break-word;">
        {description}
    </div>
</div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # 小さなボタン
    return st.button(
        "使う" if can_use else "×",
        key=f"use_{key_prefix}_{index}",
        disabled=not can_use,
        use_container_width=True,
        type="primary" if can_use else "secondary"
    )

def display_card_reward(card: dict, index: int):
    """報酬カード表示（ボタンなし）- TCGスタイル"""
    color_map = {
        ELEMENT_NONE: "#888888",
        ELEMENT_FIRE: "#FF6B6B",
        ELEMENT_WATER: "#4ECDC4",
        ELEMENT_NATURE: "#95E77D",
    }
    
    element = card.get("element", ELEMENT_NONE)
    card_type = card.get("type", CARD_ATTACK)
    color = color_map.get(element, "#888888")
    element_emoji = get_element_emoji(element)
    type_icon = CARD_TYPE_ICONS.get(card_type, "🎴")
    name = card.get('name', '')
    cost = card.get('cost', 0)
    description = card.get('description', '')
    
    card_html = f"""
<div style="background: linear-gradient(135deg, {color} 0%, {color}CC 100%); 
            border: 2px solid rgba(255, 215, 0, 0.5);
            border-radius: 8px; 
            padding: 0; 
            margin: 2px 0; 
            color: white; 
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7); 
            min-height: 130px; 
            max-height: 130px;
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
            font-size: 0.75rem;
            overflow: hidden;
            display: flex;
            flex-direction: column;">
    <div style="background: rgba(0,0,0,0.2); padding: 6px; text-align: center; flex-shrink: 0;">
        <div style="font-size: 28px; line-height: 1;">{type_icon}</div>
    </div>
    <div style="padding: 4px 8px; background: rgba(0,0,0,0.1); flex-shrink: 0;">
        <div style="font-size: 0.8rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            {element_emoji} {name}
        </div>
        <div style="font-size: 0.65rem; background: rgba(0, 0, 0, 0.3); display: inline-block; padding: 1px 4px; border-radius: 3px; margin-top: 2px;">
            ⚡{cost}
        </div>
    </div>
    <div style="padding: 3px 8px; background: rgba(0,0,0,0.2); font-size: 0.65rem; line-height: 1.3; overflow: hidden; max-height: 3.5em; flex-grow: 1; word-wrap: break-word;">
        {description}
    </div>
</div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# ===== メインゲーム =====

def main():
    st.set_page_config(page_title="デッキ構築RPG", page_icon="⚔️", layout="wide")
    
    # コンパクトなCSSを適用
    st.markdown(styles.COMPACT_CSS, unsafe_allow_html=True)
    
    # ゲーム状態の初期化
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'menu'
    
    # 現在のターンログを管理
    if 'current_turn_log' not in st.session_state:
        st.session_state.current_turn_log = []
    
    if st.session_state.game_state == 'menu':
        # セーブデータを読み込み
        if 'persistent_data' not in st.session_state:
            st.session_state.persistent_data = game_data.load_game_data()

        save_data = st.session_state.persistent_data
        total_wins = save_data.get("total_wins", 0)
        highest_floor = save_data.get("highest_floor", 0)
        upgrade_points = save_data.get("upgrade_points", 0)
        total_games = save_data.get("total_games", 0)

        # ========== タイトルバナー ==========
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2.5rem 1rem 1.5rem;
            position: relative;
        ">
            <div style="
                font-size: 0.85rem;
                letter-spacing: 0.4em;
                color: rgba(255,200,80,0.8);
                text-transform: uppercase;
                margin-bottom: 0.5rem;
                font-family: 'Courier New', monospace;
            ">✦ ROGUELIKE CARD GAME ✦</div>
            <div style="
                font-size: 3.2rem;
                font-weight: 900;
                line-height: 1;
                background: linear-gradient(135deg, #FFD700 0%, #FF8C00 40%, #FF4500 70%, #FFD700 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: none;
                filter: drop-shadow(0 0 20px rgba(255,160,0,0.5));
                margin-bottom: 0.3rem;
                font-family: 'Arial Black', sans-serif;
            ">⚔️ 異界迷宮</div>
            <div style="
                font-size: 1.1rem;
                color: rgba(255,255,255,0.6);
                letter-spacing: 0.15em;
                font-family: 'Courier New', monospace;
            ">DECK BUILDER · DUNGEON CRAWLER</div>
        </div>
        """, unsafe_allow_html=True)

        # ========== 実績バー ==========
        if total_games > 0:
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: center;
                gap: 2rem;
                padding: 0.8rem 1rem;
                margin: 0 2rem 1.5rem;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,200,80,0.2);
                border-radius: 12px;
                backdrop-filter: blur(10px);
            ">
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:900;color:#FFD700;">{total_wins}</div>
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);letter-spacing:0.1em;">WINS</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:900;color:#4ECDC4;">{highest_floor}</div>
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);letter-spacing:0.1em;">BEST FLOOR</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:900;color:#FF6B6B;">{total_games}</div>
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);letter-spacing:0.1em;">PLAYS</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:900;color:#95E77D;">💎{upgrade_points}</div>
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);letter-spacing:0.1em;">POINTS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ========== 遊び方カード ==========
        st.markdown("""
        <div style="margin: 0 0.5rem 1.5rem;">
            <div style="
                font-size: 0.7rem;
                letter-spacing: 0.3em;
                color: rgba(255,200,80,0.7);
                text-align: center;
                margin-bottom: 0.8rem;
                text-transform: uppercase;
            ">— 遊び方 —</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.6rem;">

                <div style="
                    background: linear-gradient(135deg,rgba(255,107,107,0.15),rgba(255,107,107,0.05));
                    border: 1px solid rgba(255,107,107,0.35);
                    border-radius: 12px;
                    padding: 1rem 0.8rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem;margin-bottom:0.4rem;">⚔️</div>
                    <div style="font-size:0.85rem;font-weight:700;color:#FF6B6B;margin-bottom:0.4rem;">戦闘</div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                        毎ターン <b style="color:#FFD700;">エネルギー</b> が回復。<br>
                        カードを使って敵を攻撃！<br>
                        ターン終了で敵が反撃する。
                    </div>
                </div>

                <div style="
                    background: linear-gradient(135deg,rgba(78,205,196,0.15),rgba(78,205,196,0.05));
                    border: 1px solid rgba(78,205,196,0.35);
                    border-radius: 12px;
                    padding: 1rem 0.8rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem;margin-bottom:0.4rem;">🎴</div>
                    <div style="font-size:0.85rem;font-weight:700;color:#4ECDC4;margin-bottom:0.4rem;">デッキ強化</div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                        勝利後に <b style="color:#FFD700;">カード獲得</b>。<br>
                        休憩所・ショップでも<br>
                        デッキを鍛えよう。
                    </div>
                </div>

                <div style="
                    background: linear-gradient(135deg,rgba(149,231,125,0.15),rgba(149,231,125,0.05));
                    border: 1px solid rgba(149,231,125,0.35);
                    border-radius: 12px;
                    padding: 1rem 0.8rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem;margin-bottom:0.4rem;">⚡</div>
                    <div style="font-size:0.85rem;font-weight:700;color:#95E77D;margin-bottom:0.4rem;">元素反応</div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                        炎＋水＝<b style="color:#4ECDC4;">蒸発</b>（+30)<br>
                        炎＋草＝<b style="color:#FF6B6B;">燃焼</b>（持続）<br>
                        水＋草＝<b style="color:#95E77D;">成長</b>（回復）
                    </div>
                </div>

                <div style="
                    background: linear-gradient(135deg,rgba(180,100,220,0.15),rgba(180,100,220,0.05));
                    border: 1px solid rgba(180,100,220,0.35);
                    border-radius: 12px;
                    padding: 1rem 0.8rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem;margin-bottom:0.4rem;">🗺️</div>
                    <div style="font-size:0.85rem;font-weight:700;color:#C084FC;margin-bottom:0.4rem;">ルート選択</div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                        各階層で <b style="color:#FFD700;">2択の分岐</b>。<br>
                        戦闘・休憩所・ショップ<br>
                        を戦略的に選ぼう。
                    </div>
                </div>

                <div style="
                    background: linear-gradient(135deg,rgba(255,200,80,0.15),rgba(255,200,80,0.05));
                    border: 1px solid rgba(255,200,80,0.35);
                    border-radius: 12px;
                    padding: 1rem 0.8rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem;margin-bottom:0.4rem;">❤️</div>
                    <div style="font-size:0.85rem;font-weight:700;color:#FFD700;margin-bottom:0.4rem;">HP管理</div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                        HPは戦闘をまたいで<br>
                        <b style="color:#FF6B6B;">引き継がれる</b>。<br>
                        防御カードも使おう！
                    </div>
                </div>

                <div style="
                    background: linear-gradient(135deg,rgba(100,180,255,0.15),rgba(100,180,255,0.05));
                    border: 1px solid rgba(100,180,255,0.35);
                    border-radius: 12px;
                    padding: 1rem 0.8rem;
                    text-align: center;
                ">
                    <div style="font-size:2rem;margin-bottom:0.4rem;">🔼</div>
                    <div style="font-size:0.85rem;font-weight:700;color:#60CDFF;margin-bottom:0.4rem;">永続強化</div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.7);line-height:1.5;">
                        ゲームオーバーでも<br>
                        <b style="color:#FFD700;">アップグレードは残る</b>。<br>
                        周回して強くなろう！
                    </div>
                </div>

            </div>
        </div>
        """, unsafe_allow_html=True)

        # ========== 攻略ポイント ==========
        st.markdown("""
        <div style="
            margin: 0 0.5rem 1.2rem;
            padding: 0.8rem 1rem;
            background: linear-gradient(135deg,rgba(255,200,80,0.08),rgba(255,140,0,0.05));
            border: 1px solid rgba(255,200,80,0.25);
            border-left: 3px solid #FFD700;
            border-radius: 8px;
        ">
            <div style="font-size:0.75rem;font-weight:700;color:#FFD700;margin-bottom:0.5rem;">💡 攻略のコツ</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem 1rem;">
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.75);">▶ 序盤は <b>防御カード</b> を優先してHPを温存</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.75);">▶ 元素カードを揃えると <b>反応コンボ</b> が強力</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.75);">▶ 不要カードは削除して <b>デッキを薄く</b> する</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.75);">▶ 休憩所は <b>HP全回復</b> が最も安定した選択肢</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.75);">▶ バフ中に <b>高コスト攻撃</b> を集中させると効率的</div>
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.75);">▶ ボスが近い階層では <b>ショップ</b> でHP回復を買おう</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_start, col_upgrade = st.columns(2)
        
        with col_start:
            if st.button("🎮 ゲーム開始", use_container_width=True, type="primary"):
                # 初回プレイかチェック
                save_data = st.session_state.persistent_data
                is_first_time = save_data.get("total_games", 0) == 0
                
                # 総ゲーム数を増加
                save_data["total_games"] = save_data.get("total_games", 0) + 1
                game_data.save_game_data(save_data)
                
                # アップグレードを適用
                hp_bonus = game_data.get_total_effect(save_data, "max_hp_bonus")
                energy_bonus = game_data.get_total_effect(save_data, "starting_energy_bonus")
                draw_bonus = game_data.get_total_effect(save_data, "card_draw_bonus")
                
                
                # プレイヤー初期化
                starter_deck = create_starter_deck()
                random.shuffle(starter_deck)
                
                st.session_state.player_max_hp = 100 + hp_bonus
                st.session_state.player_hp = 100 + hp_bonus
                st.session_state.shield = 0
                st.session_state.attack_buff = 0
                st.session_state.attack_buff_duration = 0
                st.session_state.rest_attack_buff = 0  # 休憩所バフ（次の1戦限り）
                st.session_state.deck = starter_deck
                st.session_state.hand = []
                st.session_state.discard = []
                st.session_state.energy = 5 + energy_bonus  # 基本5エネルギーに変更
                st.session_state.max_energy = 5 + energy_bonus
                st.session_state.all_cards = starter_deck.copy()  # 全カードリスト
                st.session_state.gold = 100  # 初期ゴールド
                
                st.session_state.turn = 0  # ツリーナビゲーション開始前
                st.session_state.battle_log = []
                st.session_state.current_turn_log = []
                
                # エフェクト用の状態変数
                st.session_state.damage_effect = None
                st.session_state.screen_shake = False
                st.session_state.screen_flash = None
                st.session_state.show_effect = False
                
                # 初回プレイフラグ
                st.session_state.show_tutorial = is_first_time
                
                # フロアツリーを生成
                nodes, root_id = floor_tree.generate_floor_tree()
                st.session_state.floor_nodes = nodes
                st.session_state.current_node_id = root_id
                
                
                # 最初のノードで初期化
                root_node = nodes[root_id]
                st.session_state.current_floor = 1
                
                # 第1階層の戦闘を開始
                setup_battle_from_node(root_node)
                st.session_state.game_state = 'battle'
                st.rerun()
        
        with col_upgrade:
            if st.button("🔼 アップグレード", use_container_width=True):
                st.session_state.game_state = 'upgrade'
                st.rerun()
    
    elif st.session_state.game_state == 'tree_selection':
        """ツリーから次の階層を選択"""
        nodes = st.session_state.floor_nodes
        current_node_id = st.session_state.current_node_id
        current_node = nodes[current_node_id]
        
        
        st.markdown(styles.COMPACT_CSS, unsafe_allow_html=True)
        
        # タイトル
        # 次の階層番号を計算（選択肢は current_node の子 = 次の階層）
        next_floor = current_node.floor_level + 1
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: white; font-size: 1.5rem; margin: 0; text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);'>
                🌳 第{next_floor}階層への道を選ぼう
            </h2>
            <div style='color: rgba(255,255,255,0.5); font-size:0.85rem; margin-top:4px;'>
                現在: 第{current_node.floor_level}階層 クリア済み
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # プレイヤーステータス
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.metric("❤️ HP", f"{st.session_state.player_hp}/{st.session_state.player_max_hp}")
        with col2:
            st.metric("🎴 デッキ", f"{len(st.session_state.all_cards)}枚")
        with col3:
            # エネルギーを5つのバーで表示
            energy_html = render_energy_bars(st.session_state.energy, st.session_state.max_energy)
            st.markdown(energy_html, unsafe_allow_html=True)

        # 休憩バフ・戦闘バフ中なら表示
        rest_buff = st.session_state.get('rest_attack_buff', 0)
        active_buff = st.session_state.attack_buff_duration >= 999
        if rest_buff > 0:
            st.info(f"💪 次の戦闘: 攻撃力+{int(rest_buff*100)}%（この戦闘限り）")
        elif active_buff:
            st.info(f"💪 戦闘バフ継続中: 攻撃力+{int(st.session_state.attack_buff*100)}%（この戦闘限り）")

        st.write("---")
        
        # ツリー表示（常時展開）
        st.write("### 🌳 マップ")
        try:
            svg_content = floor_tree.visualize_tree_graphviz(nodes, current_node_id)
            # SVGを直接markdownで表示（高さ制限）
            st.markdown(f"<div style='text-align: center; max-height: 400px; overflow: auto;'>{svg_content}</div>", unsafe_allow_html=True)
        except Exception as e:
            # Graphvizが使えない場合はテキスト表示
            text_tree = floor_tree.visualize_tree_text(nodes, current_node_id)
            st.text(text_tree)
        
        st.write("---")
        
        # 選択肢
        left_child, right_child = floor_tree.get_node_children(nodes, current_node_id)
        
        
        if left_child or right_child:
            # 左右が同じノード = 1択
            is_single_choice = (left_child and right_child and left_child.node_id == right_child.node_id)
            
            
            if is_single_choice:
                st.markdown("<h3 style='text-align: center;'>次の階層へ進む</h3>", unsafe_allow_html=True)
                
                # 中央に1つだけ表示
                col_spacer1, col_center, col_spacer2 = st.columns([1, 2, 1])
                with col_center:
                    node = left_child
                    if node.node_type == "battle":
                        st.markdown(f"## ⚔️ {node.enemy_name}\n**第{node.floor_level}階層** | 難易度: {'★' * node.difficulty}")
                    elif node.node_type == "rest":
                        st.markdown(f"## 🏘️ 休憩所\n**第{node.floor_level}階層** | HP回復 + バフ")
                    else:
                        st.markdown(f"## 🛍️ ショップ\n**第{node.floor_level}階層** | カード購入/売却")
                    
                    if st.button("→ 進む", key="choose_only", use_container_width=True, type="primary"):
                        st.session_state.current_node_id = node.node_id
                        if node.node_type == "battle":
                            setup_battle_from_node(node)
                            st.session_state.game_state = 'battle'
                        elif node.node_type == "rest":
                            st.session_state.game_state = 'rest'
                        else:
                            st.session_state.game_state = 'shop'
                        st.rerun()
            else:
                st.markdown("<h3 style='text-align: center;'>次の階層を選択</h3>", unsafe_allow_html=True)
                
                col_left, col_right = st.columns(2)
                
                if left_child:
                    with col_left:
                        if left_child.node_type == "battle":
                            st.markdown(f"## ⚔️ {left_child.enemy_name}\n**第{left_child.floor_level}階層** | 難易度: {'★' * left_child.difficulty}")
                        elif left_child.node_type == "rest":
                            st.markdown(f"## 🏘️ 休憩所\n**第{left_child.floor_level}階層** | HP回復 + バフ")
                        else:
                            st.markdown(f"## 🛍️ ショップ\n**第{left_child.floor_level}階層** | カード購入/売却")
                        
                        if st.button("← 選択", key="choose_left", use_container_width=True, type="primary"):
                            st.session_state.current_node_id = left_child.node_id
                            if left_child.node_type == "battle":
                                setup_battle_from_node(left_child)
                                st.session_state.game_state = 'battle'
                            elif left_child.node_type == "rest":
                                st.session_state.game_state = 'rest'
                            else:
                                st.session_state.game_state = 'shop'
                            st.rerun()
                
                if right_child:
                    with col_right:
                        if right_child.node_type == "battle":
                            st.markdown(f"## ⚔️ {right_child.enemy_name}\n**第{right_child.floor_level}階層** | 難易度: {'★' * right_child.difficulty}")
                        elif right_child.node_type == "rest":
                            st.markdown(f"## 🏘️ 休憩所\n**第{right_child.floor_level}階層** | HP回復 + バフ")
                        else:
                            st.markdown(f"## 🛍️ ショップ\n**第{right_child.floor_level}階層** | カード購入/売却")
                        
                        if st.button("選択 →", key="choose_right", use_container_width=True, type="primary"):
                            st.session_state.current_node_id = right_child.node_id
                            if right_child.node_type == "battle":
                                setup_battle_from_node(right_child)
                                st.session_state.game_state = 'battle'
                            elif right_child.node_type == "rest":
                                st.session_state.game_state = 'rest'
                            else:
                                st.session_state.game_state = 'shop'
                            st.rerun()
        else:
            if current_node.floor_level == 10:
                st.success("🎊 10階層到達！ゲーム完了！")
                save_data = st.session_state.persistent_data
                updated_data = game_data.record_game_result(save_data, won=True, floor_reached=10)
                st.session_state.persistent_data = updated_data
                game_data.save_game_data(updated_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 最初から", use_container_width=True, type="primary"):
                        st.session_state.game_state = 'menu'
                        st.rerun()
                with col2:
                    if st.button("🔼 アップグレード", use_container_width=True):
                        st.session_state.game_state = 'upgrade'
                        st.rerun()
        return
    
    elif st.session_state.game_state == 'rest':
        current_node = st.session_state.floor_nodes.get(st.session_state.current_node_id)
        floor_level = current_node.floor_level if current_node else "?"

        hp = st.session_state.player_hp
        max_hp = st.session_state.player_max_hp
        hp_pct = int(hp / max_hp * 100)
        deck_size = len(st.session_state.all_cards)
        gold = st.session_state.get('gold', 0)
        energy = st.session_state.energy
        max_energy = st.session_state.max_energy
        rest_buff = st.session_state.get('rest_attack_buff', 0)

        # HP割合に応じた色
        if hp_pct >= 70:
            hp_color = "#4ade80"
        elif hp_pct >= 40:
            hp_color = "#fbbf24"
        else:
            hp_color = "#f87171"

        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 1.2rem 1rem 0.5rem;
        ">
            <div style="font-size:0.7rem;letter-spacing:0.3em;color:rgba(149,231,125,0.7);text-transform:uppercase;margin-bottom:0.3rem;">
                第{floor_level}階層
            </div>
            <div style="font-size:2.2rem;font-weight:900;color:#95E77D;filter:drop-shadow(0 0 12px rgba(149,231,125,0.4));margin-bottom:0.2rem;">
                🏘️ 休憩所
            </div>
            <div style="font-size:0.8rem;color:rgba(255,255,255,0.5);">束の間の安らぎ。次の戦いに備えよ。</div>
        </div>
        """, unsafe_allow_html=True)

        # ===== プレイヤーステータスパネル =====
        st.markdown(f"""
        <div style="
            margin: 0.8rem 0.5rem 1rem;
            padding: 1rem 1.2rem;
            background: linear-gradient(135deg,rgba(20,30,20,0.9),rgba(15,25,15,0.9));
            border: 1px solid rgba(149,231,125,0.25);
            border-radius: 14px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(149,231,125,0.1);
        ">
            <div style="font-size:0.65rem;letter-spacing:0.25em;color:rgba(149,231,125,0.6);margin-bottom:0.8rem;text-transform:uppercase;">
                ▌ プレイヤーステータス
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0.8rem;align-items:center;">

                <div>
                    <div style="font-size:0.62rem;color:rgba(255,255,255,0.45);margin-bottom:0.2rem;">❤️ HP</div>
                    <div style="font-size:1.3rem;font-weight:900;color:{hp_color};">{hp}</div>
                    <div style="font-size:0.6rem;color:rgba(255,255,255,0.4);">/ {max_hp}</div>
                    <div style="margin-top:0.3rem;height:5px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden;">
                        <div style="width:{hp_pct}%;height:100%;background:{hp_color};border-radius:3px;
                            box-shadow:0 0 8px {hp_color};transition:width 0.5s;"></div>
                    </div>
                </div>

                <div>
                    <div style="font-size:0.62rem;color:rgba(255,255,255,0.45);margin-bottom:0.2rem;">⚡ エネルギー</div>
                    <div style="font-size:1.3rem;font-weight:900;color:#6ECDC4;">{energy}</div>
                    <div style="font-size:0.6rem;color:rgba(255,255,255,0.4);">/ {max_energy}</div>
                </div>

                <div>
                    <div style="font-size:0.62rem;color:rgba(255,255,255,0.45);margin-bottom:0.2rem;">🎴 デッキ</div>
                    <div style="font-size:1.3rem;font-weight:900;color:#C084FC;">{deck_size}<span style="font-size:0.7rem;font-weight:400;color:rgba(255,255,255,0.4);"> 枚</span></div>
                </div>

                <div>
                    <div style="font-size:0.62rem;color:rgba(255,255,255,0.45);margin-bottom:0.2rem;">💰 ゴールド</div>
                    <div style="font-size:1.3rem;font-weight:900;color:#FFD700;">{gold}<span style="font-size:0.7rem;font-weight:400;color:rgba(255,255,255,0.4);"> G</span></div>
                </div>

            </div>
            {"<div style='margin-top:0.8rem;padding:0.5rem 0.7rem;background:rgba(255,200,80,0.1);border:1px solid rgba(255,200,80,0.3);border-radius:8px;font-size:0.7rem;color:#FFD700;'>💪 瞑想バフ待機中: 次の戦闘中ずっと攻撃力+"+str(int(rest_buff*100))+"%</div>" if rest_buff > 0 else ""}
        </div>
        """, unsafe_allow_html=True)

        # ===== 選択カード 3択 =====
        st.markdown("""
        <div style="font-size:0.7rem;letter-spacing:0.25em;color:rgba(255,255,255,0.4);text-align:center;margin-bottom:0.8rem;text-transform:uppercase;">
            — どれか1つを選択 —
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            hp_after = min(max_hp, hp + int(max_hp * 0.4))
            heal_amt = hp_after - hp
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg,rgba(248,113,113,0.15),rgba(220,38,38,0.08));
                border: 2px solid rgba(248,113,113,0.4);
                border-radius: 14px;
                padding: 1.2rem 0.8rem;
                text-align: center;
                margin-bottom: 0.5rem;
                min-height: 160px;
            ">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">😴</div>
                <div style="font-size:1rem;font-weight:800;color:#f87171;margin-bottom:0.3rem;">就寝</div>
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.6);line-height:1.5;margin-bottom:0.5rem;">
                    HP を全回復する<br>
                    <span style="color:#4ade80;font-weight:700;">+{heal_amt} HP回復</span><br>
                    <span style="font-size:0.6rem;color:rgba(255,255,255,0.4);">{hp} → {hp_after} / {max_hp}</span>
                </div>
                <div style="font-size:0.6rem;color:rgba(255,255,255,0.35);">永続効果なし</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("😴 就寝して回復", key="rest_sleep", use_container_width=True, type="primary"):
                st.session_state.player_hp = st.session_state.player_max_hp
                proceed_to_next_floor()
                st.rerun()

        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg,rgba(192,132,252,0.15),rgba(147,51,234,0.08));
                border: 2px solid rgba(192,132,252,0.4);
                border-radius: 14px;
                padding: 1.2rem 0.8rem;
                text-align: center;
                margin-bottom: 0.5rem;
                min-height: 160px;
            ">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">🧘</div>
                <div style="font-size:1rem;font-weight:800;color:#C084FC;margin-bottom:0.3rem;">瞑想</div>
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.6);line-height:1.5;margin-bottom:0.5rem;">
                    次の1戦、攻撃力アップ<br>
                    <span style="color:#C084FC;font-weight:700;">攻撃力 +20%</span><br>
                    <span style="font-size:0.6rem;color:rgba(255,255,255,0.4);">戦闘中ずっと有効</span>
                </div>
                <div style="font-size:0.6rem;color:rgba(255,200,80,0.6);">⚠️ 次の1戦のみ</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🧘 瞑想する", key="rest_meditate", use_container_width=True, type="primary"):
                st.session_state.rest_attack_buff = max(st.session_state.get('rest_attack_buff', 0), 0.2)
                proceed_to_next_floor()
                st.rerun()

        with col3:
            attack_cards = [c for c in st.session_state.all_cards if c.get('type') == CARD_ATTACK and 'damage' in c]
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg,rgba(251,191,36,0.15),rgba(180,130,0,0.08));
                border: 2px solid rgba(251,191,36,0.4);
                border-radius: 14px;
                padding: 1.2rem 0.8rem;
                text-align: center;
                margin-bottom: 0.5rem;
                min-height: 160px;
            ">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">🧪</div>
                <div style="font-size:1rem;font-weight:800;color:#fbbf24;margin-bottom:0.3rem;">錬金術</div>
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.6);line-height:1.5;margin-bottom:0.5rem;">
                    全攻撃カードを強化する<br>
                    <span style="color:#fbbf24;font-weight:700;">攻撃力 +10%</span><br>
                    <span style="font-size:0.6rem;color:rgba(255,255,255,0.4);">対象: {len(attack_cards)}枚</span>
                </div>
                <div style="font-size:0.6rem;color:#4ade80;">✅ 永続効果</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🧪 錬金術を使う", key="rest_alchemy", use_container_width=True, type="primary"):
                for card in st.session_state.all_cards:
                    if card.get('type') == CARD_ATTACK and 'damage' in card:
                        card['damage'] = int(card['damage'] * 1.1)
                proceed_to_next_floor()
                st.rerun()

        return

    elif st.session_state.game_state == 'shop':
        st.title("🛍️ ショップ")
        st.write(f"💰 所持ゴールド: **{st.session_state.get('gold', 0)}G**")

        # P1-6: shop_cardsはshop画面に入ったときだけ初期化（ノードIDをキーに紐付け）
        shop_node_id = st.session_state.current_node_id
        if 'shop_cards' not in st.session_state or st.session_state.get('shop_node_id') != shop_node_id:
            all_cards = create_basic_cards()
            st.session_state.shop_cards = random.sample(all_cards, min(5, len(all_cards)))
            st.session_state.shop_node_id = shop_node_id
            # 各カードに価格を設定（難易度に応じて価格調整）
            current_node = st.session_state.floor_nodes.get(st.session_state.current_node_id)
            floor_bonus = (current_node.floor_level * 5) if current_node else 0
            for card in st.session_state.shop_cards:
                card['shop_price'] = 40 + floor_bonus + random.randint(0, 20)
        
        st.write("### 🎴 カード販売")
        cols = st.columns(5)
        
        for i, card in enumerate(st.session_state.shop_cards):
            with cols[i]:
                display_card_reward(card, i)
                price = card.get('shop_price', 50)
                can_afford = st.session_state.get('gold', 0) >= price
                
                if st.button(
                    f"💰 {price}G で購入" if can_afford else f"❌ {price}G",
                    key=f"buy_card_{i}",
                    use_container_width=True,
                    type="primary" if can_afford else "secondary",
                    disabled=not can_afford
                ):
                    st.session_state.gold -= price
                    st.session_state.all_cards.append(card)
                    st.session_state.shop_cards.pop(i)
                    st.success(f"✅ {card['name']}を購入しました！")
                    st.rerun()
        
        st.write("---")
        st.write("### 🎁 その他のアイテム")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background: rgba(255, 107, 107, 0.2); padding: 15px; border-radius: 10px; border: 2px solid rgba(255, 107, 107, 0.4);'>
                <div style='font-size: 2rem; text-align: center;'>❤️</div>
                <div style='font-weight: bold; text-align: center; margin: 5px 0;'>HP回復薬</div>
                <div style='font-size: 0.8rem; text-align: center; color: rgba(255,255,255,0.8);'>HP +30回復</div>
            </div>
            """, unsafe_allow_html=True)
            can_buy_potion = st.session_state.get('gold', 0) >= 30
            if st.button(
                "💰 30G で購入" if can_buy_potion else "❌ 30G",
                key="buy_potion",
                use_container_width=True,
                disabled=not can_buy_potion
            ):
                st.session_state.gold -= 30
                st.session_state.player_hp = min(
                    st.session_state.player_max_hp,
                    st.session_state.player_hp + 30
                )
                st.success("✅ HP +30回復しました！")
                st.rerun()
        
        with col2:
            st.markdown("""
            <div style='background: rgba(102, 126, 234, 0.2); padding: 15px; border-radius: 10px; border: 2px solid rgba(102, 126, 234, 0.4);'>
                <div style='font-size: 2rem; text-align: center;'>🗑️</div>
                <div style='font-weight: bold; text-align: center; margin: 5px 0;'>カード削除</div>
                <div style='font-size: 0.8rem; text-align: center; color: rgba(255,255,255,0.8);'>不要なカード1枚削除</div>
            </div>
            """, unsafe_allow_html=True)
            can_buy_remove = st.session_state.get('gold', 0) >= 40
            if st.button(
                "💰 40G で購入" if can_buy_remove else "❌ 40G",
                key="buy_remove",
                use_container_width=True,
                disabled=not can_buy_remove
            ):
                st.session_state.gold -= 40
                st.session_state.reward_choice = 'delete'
                st.session_state.cards_to_delete = []
                st.session_state.game_state = 'card_remove'
                st.rerun()
        
        with col3:
            st.markdown("""
            <div style='background: rgba(149, 231, 125, 0.2); padding: 15px; border-radius: 10px; border: 2px solid rgba(149, 231, 125, 0.4);'>
                <div style='font-size: 2rem; text-align: center;'>💎</div>
                <div style='font-weight: bold; text-align: center; margin: 5px 0;'>アップグレードポイント</div>
                <div style='font-size: 0.8rem; text-align: center; color: rgba(255,255,255,0.8);'>ポイント +3</div>
            </div>
            """, unsafe_allow_html=True)
            can_buy_points = st.session_state.get('gold', 0) >= 60
            if st.button(
                "💰 60G で購入" if can_buy_points else "❌ 60G",
                key="buy_points",
                use_container_width=True,
                disabled=not can_buy_points
            ):
                st.session_state.gold -= 60
                save_data = st.session_state.persistent_data
                save_data['upgrade_points'] = save_data.get('upgrade_points', 0) + 3
                st.session_state.persistent_data = save_data
                game_data.save_game_data(save_data)
                st.success("✅ アップグレードポイント +3 獲得！")
                st.rerun()
        
        st.write("---")
        if st.button("進む →", use_container_width=True, type="primary"):
            if 'shop_cards' in st.session_state:
                del st.session_state.shop_cards
            proceed_to_next_floor()
            st.rerun()
        return
    
    elif st.session_state.game_state == 'card_remove':
        """ショップでのカード削除画面"""
        st.title("🗑️ カード削除")
        st.write("### 削除するカードを1枚選択")
        
        # カードを種類ごとにグループ化
        card_groups = {}
        for card in st.session_state.all_cards:
            name = card['name']
            if name not in card_groups:
                card_groups[name] = []
            card_groups[name].append(card)
        
        # カード選択UI
        for name, cards in sorted(card_groups.items()):
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"**{name}** × {len(cards)}")
            with cols[1]:
                card_id = id(cards[0])
                if st.button("🗑️ 削除", key=f"remove_{card_id}", use_container_width=True):
                    st.session_state.all_cards.remove(cards[0])
                    st.success(f"✅ {name}を削除しました！")
                    st.session_state.game_state = 'shop'
                    st.rerun()
        
        st.write("---")
        if st.button("❌ キャンセル", use_container_width=True):
            st.session_state.game_state = 'shop'
            st.session_state.gold += 40  # 返金
            st.rerun()
        return
    
    elif st.session_state.game_state == 'upgrade':
        st.title("🔼 永続アップグレード")
        
        # セーブデータ
        save_data = st.session_state.persistent_data
        points = save_data.get("upgrade_points", 0)
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(241, 196, 15, 0.3) 0%, rgba(243, 156, 18, 0.3) 100%);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid rgba(241, 196, 15, 0.5);
            text-align: center;
            margin-bottom: 20px;
        '>
            <h2 style='margin: 0; color: #ffffff;'>💎 所持ポイント: {points}</h2>
            <p style='margin: 5px 0 0 0; color: rgba(255,255,255,0.8);'>ゲームをプレイして獲得しよう！</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("### 🛒 アップグレード一覧")
        st.write("ゲームオーバー後も永続的に効果が残ります。")
        
        # アップグレードを表示
        for key, info in game_data.UPGRADE_COSTS.items():
            current_level = game_data.get_upgrade_level(save_data, key)
            max_level = info["max_level"]
            
            st.write("---")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"### {info['icon']} {info['name']}")
                st.write(info['description'])
                st.write(f"**現在のレベル:** {current_level} / {max_level}")
                
                if current_level < max_level:
                    cost = info['cost'][current_level]
                    st.write(f"**次のレベルのコスト:** 💎 {cost}")
                else:
                    st.success("✅ 最大レベル達成！")
            
            with col2:
                # 効果表示
                total_effect = game_data.get_total_effect(save_data, key)
                if total_effect > 0:
                    st.metric("現在の効果", f"+{total_effect}")
                else:
                    st.write("")
            
            with col3:
                if current_level < max_level:
                    cost = info['cost'][current_level]
                    can_afford = points >= cost
                    
                    if st.button(
                        "購入" if can_afford else f"要{cost}pt",
                        key=f"buy_{key}",
                        disabled=not can_afford,
                        use_container_width=True,
                        type="primary" if can_afford else "secondary"
                    ):
                        success, message, updated_data = game_data.purchase_upgrade(save_data, key)
                        if success:
                            st.session_state.persistent_data = updated_data
                            game_data.save_game_data(updated_data)
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
        st.write("---")
        
        if st.button("⬅️ メニューに戻る", use_container_width=True):
            st.session_state.game_state = 'menu'
            st.rerun()
    
    elif st.session_state.game_state == 'battle':
        # ダメージエフェクト用のCSS・アニメーション
        damage_effect_html = ""
        screen_effect_css = ""
        
        # ダメージ数字ポップアップ（show_effectフラグがTrueの時のみ）
        if st.session_state.damage_effect and st.session_state.show_effect:
            effect = st.session_state.damage_effect
            position = "60%" if effect["type"] == "enemy" else "30%"
            
            # ダメージと元素反応を1つのテキストに統合
            damage_text = f"-{effect['amount']}"
            if effect.get('reaction'):
                damage_text = f"-{effect['amount']} {effect.get('reaction')}"
            
            damage_effect_html = f"""
            <div style='
                position: fixed;
                top: 35%;
                left: {position};
                transform: translate(-50%, -50%);
                text-align: center;
                pointer-events: none;
                z-index: 9999;
                font-size: 5rem;
                font-weight: bold;
                color: {effect["color"]};
                text-shadow: 
                    0 0 10px rgba(0,0,0,0.8),
                    0 0 20px {effect["color"]}, 
                    0 0 40px {effect["color"]},
                    2px 2px 4px rgba(0,0,0,0.9);
                animation: damagePopup 1.7s ease-out forwards;
                -webkit-text-stroke: 2px rgba(0,0,0,0.5);
            '>
                {damage_text}
            </div>
            <script>
                setTimeout(function() {{
                    var elem = document.querySelector('div[style*="damagePopup"]');
                    if (elem) elem.remove();
                }}, 1700);
            </script>
            """
            # エフェクト表示後にフラグとデータをクリア
            st.session_state.show_effect = False
            st.session_state.damage_effect = None
        
        # エネルギー消費エフェクト（同様にshow_energy_effectフラグがTrueの時のみ）
        energy_effect_html = ""
        if hasattr(st.session_state, 'energy_effect') and st.session_state.energy_effect and hasattr(st.session_state, 'show_energy_effect') and st.session_state.show_energy_effect:
            energy = st.session_state.energy_effect
            energy_text = f"-{energy['amount']}⚡"
            
            energy_effect_html = f"""
            <div style='
                position: fixed;
                top: 50%;
                left: 15%;
                transform: translate(-50%, -50%);
                text-align: center;
                pointer-events: none;
                z-index: 9998;
                font-size: 3rem;
                font-weight: bold;
                color: #FFD93D;
                text-shadow: 
                    0 0 10px rgba(0,0,0,0.8),
                    0 0 20px #FFD93D, 
                    0 0 40px #FFD93D,
                    2px 2px 4px rgba(0,0,0,0.9);
                animation: damagePopup 1.7s ease-out forwards;
                -webkit-text-stroke: 1.5px rgba(0,0,0,0.5);
            '>
                {energy_text}
            </div>
            <script>
                setTimeout(function() {{
                    var elem = document.querySelectorAll('div[style*="damagePopup"]');
                    if (elem.length > 0) elem[elem.length - 1].remove();
                }}, 1700);
            </script>
            """
            # エフェクト表示後にフラグとデータをクリア
            st.session_state.show_energy_effect = False
            st.session_state.energy_effect = None
        
        # 画面シェイク
        if st.session_state.screen_shake:
            screen_effect_css += """
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
            .main { animation: shake 0.5s ease-in-out; }
            """
            st.session_state.screen_shake = False
        
        # 画面フラッシュ
        if st.session_state.screen_flash:
            flash_color = "#ff000040" if st.session_state.screen_flash == "damage" else "#00ff0040"
            screen_effect_css += f"""
            @keyframes flash {{
                0%, 100% {{ background-color: transparent; }}
                50% {{ background-color: {flash_color}; }}
            }}
            .main::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                animation: flash 0.3s ease-out;
                pointer-events: none;
                z-index: 9998;
            }}
            """
            st.session_state.screen_flash = None
        
        # 全画面レイアウト用CSS + エフェクトCSS
        st.markdown(f"""
        <style>
        /* ダメージポップアップアニメーション */
        @keyframes damagePopup {{
            0% {{
                transform: translate(-50%, -50%) scale(0.5);
                opacity: 0;
            }}
            20% {{
                transform: translate(-50%, -70%) scale(1.2);
                opacity: 1;
            }}
            70% {{
                transform: translate(-50%, -90%) scale(1.1);
                opacity: 1;
            }}
            100% {{
                transform: translate(-50%, -120%) scale(1);
                opacity: 0;
            }}
        }}
        
        {screen_effect_css}
        
        /* ページ全体のパディングを削除 */
        .main .block-container {{
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            max-width: 100% !important;
        }}
        
        /* 要素間のマージンを削減 */
        .element-container {{
            margin: 0 !important;
        }}
        
        /* 見出しのマージンを削減 */
        h1, h2, h3, h4 {{
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
            font-size: 0.9rem !important;
        }}
        
        /* プログレスバーを小さく */
        .stProgress {{
            height: 15px !important;
        }}
        
        /* ボタンを小さく */
        .stButton > button {{
            padding: 0.3rem 0.8rem !important;
            font-size: 0.9rem !important;
        }}
        
        /* カードを小さく */
        div[style*="min-height: 140px"] {{
            min-height: 100px !important;
            padding: 10px !important;
            margin: 3px 0 !important;
        }}
        
        /* 区切り線を削除 */
        hr {{
            margin: 0.3rem 0 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # ダメージエフェクトを別のst.markdownで表示
        if damage_effect_html:
            st.markdown(damage_effect_html, unsafe_allow_html=True)
        
        # エネルギー消費エフェクトを別のst.markdownで表示
        if energy_effect_html:
            st.markdown(energy_effect_html, unsafe_allow_html=True)
        
        # ヘッダー：階層表示
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 10px;'>
            <h2 style='color: white; font-size: 1.2rem; margin: 0; text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);'>
                ⚔️ 第{st.session_state.turn}戦 ⚔️
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 初回プレイ時のチュートリアル
        if hasattr(st.session_state, 'show_tutorial') and st.session_state.show_tutorial:
            st.info("""
            📚 **チュートリアル**
            
            - 🗑️ **手札破棄**: ターン終了時、使わなかったカードは全て破棄されます
            - ⏳ **元素反応**: 元素反応後、1ターンは新しい元素が付着しません
            - 🎴 **ドローカード**: 選択肢を増やすため、ドローカードを積極的に使いましょう
            - 💎 **エネルギー**: 毎ターン5エネルギーで複数のカードを使用できます
            """)
            
            if st.button("✅ 理解しました", use_container_width=True, type="primary"):
                st.session_state.show_tutorial = False
                st.rerun()
        
        # 上部：プレイヤーと敵（2カラムで横幅たっぷり）
        col1, col2 = st.columns(2)
        
        with col1:
            # プレイヤー画像とステータス
            player_image = """
            <div style='text-align: center; margin-bottom: 10px;'>
                <div style='
                    width: 80px;
                    height: 80px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 3rem;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                    border: 3px solid rgba(255, 255, 255, 0.3);
                '>
                    🧙
                </div>
                <div style='color: white; font-weight: bold; margin-top: 5px; font-size: 0.9rem;'>プレイヤー</div>
            </div>
            """
            st.markdown(player_image, unsafe_allow_html=True)
            
            # プレイヤーステータス（コンパクト）
            hp_ratio = st.session_state.player_hp / st.session_state.player_max_hp
            st.progress(max(0, hp_ratio), text=f"❤️ HP: {st.session_state.player_hp}/{st.session_state.player_max_hp}")
            
            # エネルギーを5つのバーで表示
            energy_html = render_energy_bars(st.session_state.energy, st.session_state.max_energy)
            st.markdown(energy_html, unsafe_allow_html=True)
            
            # 詳細ステータス情報を整理
            status_parts = []
            
            if st.session_state.shield > 0:
                status_parts.append(f"🛡️{st.session_state.shield}")
            
            if st.session_state.attack_buff_duration > 0:
                buff_percent = int(st.session_state.attack_buff * 100)
                if st.session_state.attack_buff_duration >= 999:
                    status_parts.append(f"💪+{buff_percent}% (この戦闘限り)")
                else:
                    status_parts.append(f"💪+{buff_percent}% ({st.session_state.attack_buff_duration}T)")
            
            if status_parts:
                st.caption(" | ".join(status_parts))
            
            # 追加情報（デッキ、クールダウン）
            info_parts = [f"📚山札:{len(st.session_state.deck)} 🗑️捨札:{len(st.session_state.discard)}"]
            
            if hasattr(st.session_state, 'element_reaction_cooldown') and st.session_state.element_reaction_cooldown > 0:
                info_parts.append(f"⏳反応CD:{st.session_state.element_reaction_cooldown}T")
            
            st.caption(" | ".join(info_parts))
        
        with col2:
            # 敵画像とステータス
            enemy_emoji = get_enemy_emoji(st.session_state.enemy["name"])
            enemy_image = f"""
            <div style='text-align: center; margin-bottom: 10px;'>
                <div style='
                    width: 80px;
                    height: 80px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 3rem;
                    box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    animation: enemyPulse 2s ease-in-out infinite;
                '>
                    {enemy_emoji}
                </div>
                <div style='color: white; font-weight: bold; margin-top: 5px; font-size: 0.9rem;'>{st.session_state.enemy["name"]}</div>
            </div>
            <style>
                @keyframes enemyPulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                }}
            </style>
            """
            st.markdown(enemy_image, unsafe_allow_html=True)
            
            # 敵ステータス（コンパクト）
            enemy_hp_ratio = max(0, st.session_state.enemy["hp"] / st.session_state.enemy["max_hp"])
            st.progress(enemy_hp_ratio, text=f"❤️ HP: {max(0, st.session_state.enemy['hp'])}/{st.session_state.enemy['max_hp']}")
            
            # 次の行動（コンパクト）
            action_desc, action_icon = get_action_description(st.session_state.enemy["next_action"])
            
            # 攻撃の場合はダメージ数を表示
            if st.session_state.enemy["next_action"] == "attack":
                damage = st.session_state.enemy["attack"]
                enemy_status = f"{action_icon} 次:{action_desc}({damage})"
            elif st.session_state.enemy["next_action"] == "big_attack":
                damage = int(st.session_state.enemy["attack"] * 1.5)
                enemy_status = f"{action_icon} 次:{action_desc}({damage})"
            elif st.session_state.enemy["next_action"] == "defend":
                shield = int(st.session_state.enemy["attack"] * 1.2)
                enemy_status = f"{action_icon} 次:{action_desc}(+{shield})"
            else:
                enemy_status = f"{action_icon} 次:{action_desc}"
            
            # シールド表示
            if st.session_state.enemy["shield"] > 0:
                enemy_status += f" 🛡️{st.session_state.enemy['shield']}"
            
            # 元素反応クールダウン表示（敵側）
            if hasattr(st.session_state, 'element_reaction_cooldown') and st.session_state.element_reaction_cooldown > 0:
                enemy_status += f" ⏳反応CD:{st.session_state.element_reaction_cooldown}T"
            
            # 元素付与状態（持続ターン表示）
            if st.session_state.enemy["element"]:
                emoji = get_element_emoji(st.session_state.enemy["element"])
                if st.session_state.enemy["element_duration"] > 0:
                    enemy_status += f" {emoji}×{st.session_state.enemy['element_duration']}T"
                else:
                    enemy_status += f" {emoji}"

            # 燃焼状態（持続ターン表示）
            if st.session_state.enemy["burn_duration"] > 0:
                enemy_status += f" 🔥×{st.session_state.enemy['burn_duration']}T"

            # デバフ状態表示
            if st.session_state.enemy.get("poison_duration", 0) > 0:
                enemy_status += f" ☠️×{st.session_state.enemy['poison_duration']}T"
            if st.session_state.enemy.get("debuff_weaken_duration", 0) > 0:
                weaken_pct = int(st.session_state.enemy.get("debuff_weaken", 0) * 100)
                enemy_status += f" ⬇️-{weaken_pct}%×{st.session_state.enemy['debuff_weaken_duration']}T"
            if st.session_state.enemy.get("stunned", False):
                enemy_status += " 💫スタン"

            st.caption(enemy_status)
        
        # 勝敗判定  敵を倒した場合
        if st.session_state.enemy["hp"] <= 0:
            st.session_state.show_effect = False
            st.session_state.game_state = 'victory'
            # P2-9: ゴールド報酬を難易度ベースに調整（floor_levelと敵難易度を参照）
            current_node = st.session_state.floor_nodes.get(st.session_state.current_node_id)
            floor_level = current_node.floor_level if current_node else st.session_state.turn
            difficulty = current_node.difficulty if current_node else 1
            gold_earned = 15 + floor_level * 8 + difficulty * 3 + random.randint(0, 10)
            st.session_state.prev_gold = st.session_state.get('gold', 0)
            st.session_state.gold = st.session_state.prev_gold + gold_earned
            st.rerun()
            return
        
        if st.session_state.player_hp <= 0:
            # 敗北画面
            st.error("💀 敗北")
            
            save_data = st.session_state.persistent_data
            floor_reached = st.session_state.get('current_floor', st.session_state.turn)
            updated_data = game_data.record_game_result(save_data, won=False, floor_reached=floor_reached)
            st.session_state.persistent_data = updated_data
            game_data.save_game_data(updated_data)
            
            points_earned = max(1, floor_reached // 2)
            st.caption(f"到達階層:{floor_reached} 獲得:💎{points_earned}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 最初から", use_container_width=True, type="primary"):
                    st.session_state.game_state = 'menu'
                    st.rerun()
            with col2:
                if st.button("🔼 アップグレード", use_container_width=True):
                    st.session_state.game_state = 'upgrade'
                    st.rerun()
            return
        
        # 中央：手札（横1列・コンパクト）
        # エネルギーを描画前にクランプして不整合を防ぐ
        st.session_state.energy = max(0, min(st.session_state.energy, st.session_state.max_energy))

        if len(st.session_state.hand) == 0:
            st.caption("手札なし")
        else:
            cols = st.columns(len(st.session_state.hand))
            card_played = False  # 1ループで1枚だけ使えるようにするフラグ
            for i, card in enumerate(st.session_state.hand):
                with cols[i]:
                    if display_card_compact(card, "hand", i) and not card_played:
                        card_played = True
                        st.session_state.current_turn_log = []
                        log_before = len(st.session_state.battle_log)
                        play_card(i)
                        log_after = len(st.session_state.battle_log)
                        st.session_state.current_turn_log = st.session_state.battle_log[log_before:log_after]
                        st.rerun()
        
        # 下部：ターンログ（コンパクト）
        if st.session_state.current_turn_log:
            recent_logs = st.session_state.current_turn_log[-3:]
            st.caption("📝 " + " | ".join(recent_logs))
        
        # ターン終了ボタン（ターンログの直下）
        if st.button("🔚 ターン終了", key="end_turn_main", use_container_width=True, type="primary"):
            # ターンログをリセット
            st.session_state.current_turn_log = []
            
            # 手札を全て捨て札へ（Slay the Spire式）
            if len(st.session_state.hand) > 0:
                discard_count = len(st.session_state.hand)
                st.session_state.discard.extend(st.session_state.hand)
                st.session_state.hand = []
                st.session_state.battle_log.append(f"🗑️ {discard_count}枚のカードを破棄")
            
            # ログ数を記録
            log_before = len(st.session_state.battle_log)
            
            # 敵が生きている場合のみ敵のターン
            if st.session_state.enemy["hp"] > 0:
                enemy_turn()
            
            # 敵のターンログをターンログに追加（新しく追加された分のみ）
            log_after = len(st.session_state.battle_log)
            st.session_state.current_turn_log = st.session_state.battle_log[log_before:log_after]
            
            # 次のターン開始
            start_turn()
            
            st.rerun()
        
        st.write("---")
        
        # 情報パネル：3つのエクスパンダーを横並び
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            with st.expander("🎴 デッキ＆カード"):
                st.metric("山札", f"{len(st.session_state.deck)}枚")
                st.metric("捨札", f"{len(st.session_state.discard)}枚")
                st.write("**所持カード一覧:**")
                card_counts = {}
                for card in st.session_state.all_cards:
                    name = card['name']
                    card_counts[name] = card_counts.get(name, 0) + 1
                
                for name, count in sorted(card_counts.items()):
                    st.caption(f"{name} × {count}")
        
        with info_col2:
            with st.expander("⚡ 元素反応＆デバフガイド"):
                st.markdown("""
                <div style='font-size: 0.8rem;'>
                    <div style='background: rgba(255, 107, 107, 0.3); padding: 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #FF6B6B;'>
                        <strong>🔥 燃焼</strong> 炎 + 草: 追加+12 | 持続10×3T
                    </div>
                    <div style='background: rgba(78, 205, 196, 0.3); padding: 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #4ECDC4;'>
                        <strong>💧 蒸発</strong> 炎 + 水: 追加+30 高威力！
                    </div>
                    <div style='background: rgba(149, 231, 125, 0.3); padding: 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #95E77D;'>
                        <strong>🌿 成長</strong> 水 + 草: 追加+25 | HP回復12%
                    </div>
                    <div style='background: rgba(180, 100, 220, 0.3); padding: 8px; border-radius: 6px; margin-bottom: 4px; border-left: 3px solid #b464dc;'>
                        <strong>💀 デバフカード</strong><br>
                        ⬇️ 弱体化: 敵攻撃力ダウン<br>
                        💫 スタン: 1T行動不能<br>
                        ☠️ 毒: 毎T継続ダメージ<br>
                        ❄️ 氷結: 弱体化 + 水付与
                    </div>
                    <p style='margin-top: 6px; font-size: 0.75rem; color: rgba(255,255,255,0.7);'>
                        ⏳ 反応後1ターンは元素付着不可
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with info_col3:
            with st.expander("📜 戦闘ログ"):
                st.write("**最新20件:**")
                for log in st.session_state.battle_log[-20:]:
                    st.caption(log)
    
    elif st.session_state.game_state == 'clear':
        """ゲームクリア画面"""
        st.markdown("""
        <div style='text-align: center; padding: 40px 0;'>
            <div style='font-size: 4rem; margin-bottom: 20px;'>🎉</div>
            <h1 style='color: #FFD700; font-size: 3rem; text-shadow: 0 0 20px rgba(255, 215, 0, 0.8); margin-bottom: 10px;'>
                ゲームクリア！
            </h1>
            <h2 style='color: #FFA500; font-size: 1.8rem; text-shadow: 0 0 10px rgba(255, 165, 0, 0.6);'>
                10階層を制覇しました！
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 統計情報
        st.write("---")
        st.write("### 📊 クリア統計")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("到達階層", "10")
        with col2:
            st.metric("獲得ゴールド", st.session_state.get('gold', 0))
        with col3:
            st.metric("デッキサイズ", len(st.session_state.all_cards))
        
        # 永続データ更新
        save_data = st.session_state.persistent_data
        save_data['total_wins'] = save_data.get('total_wins', 0) + 1
        save_data['highest_floor'] = 10
        st.session_state.persistent_data = save_data
        game_data.save_game_data(save_data)
        
        # ボタン
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 メニューに戻る", use_container_width=True, type="primary"):
                st.session_state.game_state = 'menu'
                st.rerun()
        with col2:
            if st.button("🔼 アップグレード", use_container_width=True):
                st.session_state.game_state = 'upgrade'
                st.rerun()
        
        return
    
    elif st.session_state.game_state == 'victory':
        """勝利画面：報酬選択"""
        st.success(f"🎉 勝利！ {st.session_state.enemy['name']}を倒した")
        st.info(f"💰 ゴールド +{st.session_state.gold - st.session_state.get('prev_gold', 0)} (所持: {st.session_state.gold}G)")
        
        # 報酬選択の状態管理
        if 'reward_choice' not in st.session_state:
            st.session_state.reward_choice = None
        if 'cards_to_delete' not in st.session_state:
            st.session_state.cards_to_delete = []
        
        # 報酬選択画面
        if st.session_state.reward_choice is None:
            st.write("### 🎁 報酬を選択してください")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    border: 2px solid rgba(102, 126, 234, 0.5);
                '>
                    <div style='font-size: 3rem;'>✨</div>
                    <div style='font-size: 1.2rem; font-weight: bold; margin: 10px 0;'>カード獲得</div>
                    <div style='font-size: 0.9rem; color: rgba(255, 255, 255, 0.8);'>新しいカードを1枚獲得</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✨ カード獲得", key="choose_card", use_container_width=True, type="primary"):
                    st.session_state.reward_choice = 'card'
                    st.rerun()
            
            with col2:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, rgba(255, 107, 107, 0.3) 0%, rgba(238, 90, 111, 0.3) 100%);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    border: 2px solid rgba(255, 107, 107, 0.5);
                '>
                    <div style='font-size: 3rem;'>🗑️</div>
                    <div style='font-size: 1.2rem; font-weight: bold; margin: 10px 0;'>カード削除</div>
                    <div style='font-size: 0.9rem; color: rgba(255, 255, 255, 0.8);'>不要なカードを最大2枚削除</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ カード削除", key="choose_delete", use_container_width=True):
                    st.session_state.reward_choice = 'delete'
                    st.rerun()
            
            with col3:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, rgba(240, 147, 251, 0.3) 0%, rgba(245, 87, 108, 0.3) 100%);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    border: 2px solid rgba(240, 147, 251, 0.5);
                '>
                    <div style='font-size: 3rem;'>💎</div>
                    <div style='font-size: 1.2rem; font-weight: bold; margin: 10px 0;'>ポイント獲得</div>
                    <div style='font-size: 0.9rem; color: rgba(255, 255, 255, 0.8);'>アップグレードポイント+5</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("💎 ポイント獲得", key="choose_points", use_container_width=True):
                    # ポイント付与
                    save_data = st.session_state.persistent_data
                    save_data['upgrade_points'] = save_data.get('upgrade_points', 0) + 5
                    st.session_state.persistent_data = save_data
                    game_data.save_game_data(save_data)
                    # 次の階層へ
                    proceed_to_next_floor()
                    st.rerun()
            return
        
        # カード獲得画面（P0-2: 報酬カードをセッションキャッシュ化）
        elif st.session_state.reward_choice == 'card':
            if 'reward_cards_cache' not in st.session_state:
                all_cards = create_basic_cards()
                st.session_state.reward_cards_cache = random.sample(all_cards, min(3, len(all_cards)))
            reward_cards = st.session_state.reward_cards_cache

            st.write("### ✨ カードを1枚選択")
            cols = st.columns(3)
            for i, card in enumerate(reward_cards):
                with cols[i]:
                    display_card_reward(card, i)

                    if st.button(f"✨ 獲得", key=f"get_reward_{i}", use_container_width=True, type="primary"):
                        st.session_state.all_cards.append(card)
                        st.session_state.reward_choice = None
                        if 'reward_cards_cache' in st.session_state:
                            del st.session_state.reward_cards_cache
                        proceed_to_next_floor()
                        st.rerun()
            return

        # カード削除画面（P0-3: インデントバグ修正）
        elif st.session_state.reward_choice == 'delete':
            st.write("### 🗑️ 削除するカードを選択（最大2枚）")
            st.caption(f"現在のデッキ: {len(st.session_state.all_cards)}枚 | 選択中: {len(st.session_state.cards_to_delete)}/2枚")

            card_groups = {}
            for card in st.session_state.all_cards:
                name = card['name']
                if name not in card_groups:
                    card_groups[name] = []
                card_groups[name].append(card)

            for name, cards in sorted(card_groups.items()):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"**{name}** × {len(cards)}")
                with cols[1]:
                    card_id = id(cards[0])
                    if card_id in st.session_state.cards_to_delete:
                        if st.button("✅ 選択中", key=f"unselect_{card_id}", use_container_width=True):
                            st.session_state.cards_to_delete.remove(card_id)
                            st.rerun()
                    else:
                        disabled = len(st.session_state.cards_to_delete) >= 2 or len(st.session_state.all_cards) <= 10
                        if st.button("🗑️ 選択", key=f"select_{card_id}", use_container_width=True, disabled=disabled):
                            st.session_state.cards_to_delete.append(card_id)
                            st.rerun()

            if len(st.session_state.all_cards) <= 10:
                st.warning("⚠️ デッキは最低10枚必要です")

            st.write("---")
            col_cancel, col_confirm = st.columns(2)

            with col_cancel:
                if st.button("❌ キャンセル", use_container_width=True):
                    st.session_state.reward_choice = None
                    st.session_state.cards_to_delete = []
                    st.rerun()

            with col_confirm:
                if st.button(f"🗑️ {len(st.session_state.cards_to_delete)}枚削除して次へ",
                             use_container_width=True,
                             type="primary",
                             disabled=len(st.session_state.cards_to_delete) == 0):
                    for card_id in st.session_state.cards_to_delete:
                        for card in st.session_state.all_cards:
                            if id(card) == card_id:
                                st.session_state.all_cards.remove(card)
                                break
                    st.session_state.cards_to_delete = []
                    st.session_state.reward_choice = None
                    proceed_to_next_floor()
                    st.rerun()

            return

if __name__ == "__main__":
    main()