"""
ゲームデータの永続化と管理
"""
import json
import os
from typing import Dict, List, Any

SAVE_FILE = "save_data.json"

# デフォルトのアップグレードデータ
DEFAULT_UPGRADES = {
    "max_hp_bonus": 0,          # 最大HP増加
    "starting_energy_bonus": 0,  # 初期エネルギー増加
    "card_draw_bonus": 0,        # 初期ドロー枚数増加
    "total_wins": 0,             # 総勝利数
    "highest_floor": 0,          # 最高到達階層
    "total_games": 0,            # 総ゲーム数
    "upgrade_points": 0,         # アップグレードポイント
}

# アップグレードのコストと効果
UPGRADE_COSTS = {
    "max_hp_bonus": {
        "cost": [5, 10, 15, 20, 30],  # レベルごとのコスト
        "effect": 10,                  # 1レベルあたりの効果
        "max_level": 5,
        "name": "最大HP増加",
        "description": "最大HPが+10される",
        "icon": "❤️"
    },
    "starting_energy_bonus": {
        "cost": [10, 20],  # Lv2まで（Lv3を削除）
        "effect": 1,
        "max_level": 2,  # 最大Lv2に変更
        "name": "初期エネルギー増加",
        "description": "開始時のエネルギーが+1される",
        "icon": "⚡"
    },
    "card_draw_bonus": {
        "cost": [8, 16, 24],
        "effect": 1,
        "max_level": 3,
        "name": "初期ドロー枚数増加",
        "description": "初期手札が+1枚される",
        "icon": "🎴"
    },
}

def load_game_data() -> Dict[str, Any]:
    """セーブデータを読み込む"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 新しいキーがあれば追加
                for key, value in DEFAULT_UPGRADES.items():
                    if key not in data:
                        data[key] = value
                return data
        except Exception as e:
            print(f"セーブデータ読み込みエラー: {e}")
            return DEFAULT_UPGRADES.copy()
    return DEFAULT_UPGRADES.copy()

def save_game_data(data: Dict[str, Any]) -> bool:
    """セーブデータを保存"""
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"セーブデータ保存エラー: {e}")
        return False

def add_upgrade_points(data: Dict[str, Any], points: int) -> Dict[str, Any]:
    """アップグレードポイントを追加"""
    data["upgrade_points"] += points
    return data

def purchase_upgrade(data: Dict[str, Any], upgrade_key: str) -> tuple[bool, str, Dict[str, Any]]:
    """アップグレードを購入"""
    if upgrade_key not in UPGRADE_COSTS:
        return False, "不明なアップグレード", data
    
    upgrade_info = UPGRADE_COSTS[upgrade_key]
    current_level = data.get(upgrade_key, 0)
    
    # 最大レベルチェック
    if current_level >= upgrade_info["max_level"]:
        return False, "最大レベルに達しています", data
    
    # コストチェック
    cost = upgrade_info["cost"][current_level]
    if data["upgrade_points"] < cost:
        return False, f"ポイント不足（必要: {cost}）", data
    
    # 購入処理
    data["upgrade_points"] -= cost
    data[upgrade_key] = current_level + 1
    
    return True, f"{upgrade_info['name']} Lv.{current_level + 1} を購入しました！", data

def record_game_result(data: Dict[str, Any], won: bool, floor_reached: int) -> Dict[str, Any]:
    """ゲーム結果を記録"""
    data["total_games"] += 1
    
    if won:
        data["total_wins"] += 1
        # 勝利時はフロア数に応じてポイント付与
        points = floor_reached * 2
        data["upgrade_points"] += points
    else:
        # 敗北時もフロア数に応じて少しポイント付与
        points = max(1, floor_reached // 2)
        data["upgrade_points"] += points
    
    # 最高記録更新
    if floor_reached > data["highest_floor"]:
        data["highest_floor"] = floor_reached
        data["upgrade_points"] += 5  # 記録更新ボーナス
    
    return data

def get_upgrade_level(data: Dict[str, Any], upgrade_key: str) -> int:
    """アップグレードの現在のレベルを取得"""
    return data.get(upgrade_key, 0)

def get_total_effect(data: Dict[str, Any], upgrade_key: str) -> int:
    """アップグレードの合計効果を取得"""
    level = get_upgrade_level(data, upgrade_key)
    if upgrade_key in UPGRADE_COSTS:
        return level * UPGRADE_COSTS[upgrade_key]["effect"]
    return 0

def reset_all_upgrades(data: Dict[str, Any]) -> Dict[str, Any]:
    """全てのアップグレードをリセット（デバッグ用）"""
    return DEFAULT_UPGRADES.copy()