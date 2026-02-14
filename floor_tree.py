"""
フロアツリーの生成とビジュアル化
毎ゲーム異なるランダムツリーを生成し、プレイヤーが2択で選択できる
"""

import random
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

# ===== ノード定義 =====

@dataclass
class FloorNode:
    """フロアツリーのノード"""
    node_id: str              # 一意のID: "level_0_0", "level_1_0", ...
    floor_level: int          # 階層: 1-10
    node_type: str            # "battle" | "rest" | "shop"
    difficulty: int           # 敵の難易度: 1-10（node_typeが"battle"の時のみ）
    enemy_name: Optional[str] # 敵名
    parent_id: Optional[str]  = None
    left_child_id: Optional[str] = None
    right_child_id: Optional[str] = None
    visited: bool = False


# ===== ツリー生成エンジン =====

ENEMY_NAMES = ["スライム", "ゴブリン", "オーク", "ドラゴン", "魔法使い"]

def get_enemy_for_difficulty(difficulty: int) -> str:
    """難易度に応じて敵を選択"""
    # 難易度1-2: スライム
    # 難易度3-4: ゴブリン
    # 難易度5-6: オーク
    # 難易度7-8: ドラゴン
    # 難易度9-10: 魔法使い
    if difficulty <= 2:
        return "スライム"
    elif difficulty <= 4:
        return "ゴブリン"
    elif difficulty <= 6:
        return "オーク"
    elif difficulty <= 8:
        return "ドラゴン"
    else:
        return "魔法使い"


def decide_node_type(floor_level: int) -> str:
    """階層に応じてノードタイプを決定"""
    if floor_level == 10:
        return "battle"  # 最終階層は必ず敵
    
    # 60%: 敵, 20%: 休憩, 20%: ショップ
    rand = random.random()
    if rand < 0.6:
        return "battle"
    elif rand < 0.8:
        return "rest"
    else:
        return "shop"


def generate_floor_tree(seed: Optional[int] = None) -> Tuple[Dict[str, FloorNode], str]:
    """
    ランダムツリー生成（スリム分岐型）
    階層ごとに1択または2択をランダムに配置。肥大化を防ぐ
    
    Returns:
        (ノード辞書, ルートノードID)
    """
    if seed is not None:
        random.seed(seed)
    
    nodes = {}
    node_counter = 0
    
    def create_node(floor_level: int, parent_id: Optional[str] = None) -> FloorNode:
        """ノードを生成"""
        nonlocal node_counter
        node_id = f"node_{node_counter}"
        node_counter += 1
        
        # ノードタイプを決定
        if floor_level == 1:
            node_type = "battle"  # 第1階層は必ず戦闘
        elif floor_level == 10:
            node_type = "battle"  # 最終階層は必ずボス
        else:
            node_type = decide_node_type(floor_level)
        
        # 難易度
        if floor_level == 1:
            difficulty = 1
        else:
            base_difficulty = floor_level + random.randint(-1, 2)
            difficulty = max(1, min(base_difficulty, 10))
        
        # 敵名
        enemy_name = get_enemy_for_difficulty(difficulty) if node_type == "battle" else None
        
        node = FloorNode(
            node_id=node_id,
            floor_level=floor_level,
            node_type=node_type,
            difficulty=difficulty,
            enemy_name=enemy_name,
            parent_id=parent_id
        )
        
        nodes[node_id] = node
        return node
    
    def generate_path(parent_node: FloorNode, max_depth: int = 10):
        """一本道のパスを生成（分岐は確率的）"""
        if parent_node.floor_level >= max_depth:
            return
        
        next_floor = parent_node.floor_level + 1
        
        # 分岐確率を決定（階層が深いほど低く）
        # 階層2-3: 80%で2択、20%で1択
        # 階層4-6: 60%で2択、40%で1択
        # 階層7-9: 40%で2択、60%で1択
        if next_floor <= 3:
            branch_chance = 0.8
        elif next_floor <= 6:
            branch_chance = 0.6
        else:
            branch_chance = 0.4
        
        # 分岐するかどうか決定
        should_branch = random.random() < branch_chance
        
        if should_branch:
            # 2択を生成
            left_child = create_node(next_floor, parent_node.node_id)
            right_child = create_node(next_floor, parent_node.node_id)
            
            parent_node.left_child_id = left_child.node_id
            parent_node.right_child_id = right_child.node_id
            
            # それぞれのパスを再帰的に生成
            generate_path(left_child, max_depth)
            generate_path(right_child, max_depth)
        else:
            # 1択のみ生成
            only_child = create_node(next_floor, parent_node.node_id)
            
            # 左右両方に同じノードを設定（1択として表示）
            parent_node.left_child_id = only_child.node_id
            parent_node.right_child_id = only_child.node_id
            
            # パスを続ける
            generate_path(only_child, max_depth)
    
    # ルートノードを生成
    root = create_node(floor_level=1)
    root_id = root.node_id
    
    # ツリーを生成（階層10まで）
    generate_path(root, max_depth=10)
    
    return nodes, root_id


def get_node_children(nodes: Dict[str, FloorNode], node_id: str) -> Tuple[Optional[FloorNode], Optional[FloorNode]]:
    """ノードの左右の子を取得"""
    node = nodes.get(node_id)
    if not node:
        return None, None
    
    left_child = nodes.get(node.left_child_id) if node.left_child_id else None
    right_child = nodes.get(node.right_child_id) if node.right_child_id else None
    
    return left_child, right_child


def get_node_by_id(nodes: Dict[str, FloorNode], node_id: str) -> Optional[FloorNode]:
    """IDからノードを取得"""
    return nodes.get(node_id)


# ===== ビジュアル化関数 =====

def get_visible_nodes(nodes: Dict[str, FloorNode], current_node_id: str, depth: int = 2) -> Dict[str, FloorNode]:
    """
    現在のノードから到達可能なノードのみを抽出
    
    Args:
        nodes: 全ノード辞書
        current_node_id: 現在のノードID
        depth: 表示する深さ（デフォルト2=次の次の階層まで）
    
    Returns:
        到達可能なノード辞書
    """
    current_node = nodes[current_node_id]
    visible_nodes = {current_node_id: current_node}
    
    # 再帰的に到達可能なノードを収集
    def add_reachable_nodes(node_id: str, remaining_depth: int):
        if remaining_depth <= 0 or node_id not in nodes:
            return
        
        node = nodes[node_id]
        
        # 左右の子ノードを追加（重複を避ける）
        child_ids = set()
        if node.left_child_id:
            child_ids.add(node.left_child_id)
        if node.right_child_id:
            child_ids.add(node.right_child_id)
        
        for child_id in child_ids:
            if child_id not in visible_nodes:
                visible_nodes[child_id] = nodes[child_id]
                add_reachable_nodes(child_id, remaining_depth - 1)
    
    add_reachable_nodes(current_node_id, depth)
    return visible_nodes


def visualize_tree_graphviz(nodes: Dict[str, FloorNode], current_node_id: str) -> str:
    """
    graphvizでツリーを可視化してSVGを返す（2階層先までのみ表示）
    
    Args:
        nodes: ノード辞書
        current_node_id: 現在のノードID
    
    Returns:
        SVG文字列
    """
    try:
        import graphviz
        import os
    except ImportError:
        # graphvizがインストールされていない場合はテキスト表示
        return visualize_tree_text(nodes, current_node_id)
    
    # Graphvizの実行ファイルパスを明示的に設定
    if os.name == 'nt':  # Windows
        possible_paths = [
            r"C:\Program Files (x86)\Graphviz\bin",
            r"C:\Program Files\Graphviz\bin",
        ]
        for gv_path in possible_paths:
            if os.path.exists(gv_path):
                os.environ["PATH"] = gv_path + os.pathsep + os.environ.get("PATH", "")
                # graphvizモジュールに直接パスを設定
                try:
                    import graphviz.backend as gb
                    gb.DOT_BINARY = os.path.join(gv_path, "dot.exe")
                except:
                    pass
                break
    
    # 表示するノードをフィルタリング（2階層先まで）
    visible_nodes = get_visible_nodes(nodes, current_node_id, depth=2)
    
    # graphvizオブジェクト作成
    dot = graphviz.Digraph('floor_tree', format='svg')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='rounded,filled', fontname='MS Gothic', fontsize='9')
    dot.attr('graph', bgcolor='transparent')
    
    # ノードを追加
    for node_id, node in sorted(visible_nodes.items()):
        # ノード表示
        if node.node_type == "battle":
            label = f"{node.enemy_name}\n⭐ Lv.{node.difficulty}"
        elif node.node_type == "rest":
            label = f"休憩所\n🏘️"
        else:  # shop
            label = f"ショップ\n🛍️"
        
        # ツールチップ（ホバー時表示）: 階層名
        tooltip = f"第{node.floor_level}階層"
        
        # 色分け
        if node_id == current_node_id:
            color = '#FF6B6B'  # 赤: 現在位置
            penwidth = '3'
        elif node.node_type == "battle":
            color = '#FFD93D'  # 金: 戦闘
            penwidth = '1'
        elif node.node_type == "rest":
            color = '#6BCB77'  # 緑: 休憩
            penwidth = '1'
        else:  # shop
            color = '#4D96FF'  # 青: ショップ
            penwidth = '1'
        
        dot.node(node_id, label, fillcolor=color, penwidth=penwidth, fontcolor='white', tooltip=tooltip)
    
    # エッジを追加（重複を避ける）
    for node_id, node in visible_nodes.items():
        # 左右の子ノードをセットで管理（重複排除）
        child_ids = set()
        if node.left_child_id and node.left_child_id in visible_nodes:
            child_ids.add(node.left_child_id)
        if node.right_child_id and node.right_child_id in visible_nodes:
            child_ids.add(node.right_child_id)
        
        # 重複しない子ノードへのエッジを追加
        for child_id in child_ids:
            dot.edge(node_id, child_id, color='gray80', penwidth='1.5')
    
    # SVG文字列を返す
    try:
        svg_string = dot.pipe(format='svg').decode('utf-8')
        return svg_string
    except Exception as e:
        print(f"graphviz error: {e}")
        return visualize_tree_text(nodes, current_node_id)


def visualize_tree_text(nodes: Dict[str, FloorNode], current_node_id: str) -> str:
    """
    テキスト形式のツリー表示（2階層先までのみ）
    """
    current_node = nodes[current_node_id]
    current_floor = current_node.floor_level
    
    result = "🌳 フロアツリー（次の次の階層まで表示）\n"
    result += "=" * 40 + "\n\n"
    
    # 現在の階層から2階層先までを表示
    for floor in range(current_floor, min(current_floor + 3, 11)):
        result += f"【第{floor}階層】\n"
        nodes_in_floor = [n for n in nodes.values() if n.floor_level == floor]
        
        for node in sorted(nodes_in_floor, key=lambda x: int(x.node_id.split('_')[-1])):
            marker = "→ " if node.node_id == current_node_id else "   "
            
            if node.node_type == "battle":
                result += f"{marker}🔥 {node.enemy_name} (Lv.{node.difficulty})\n"
            elif node.node_type == "rest":
                result += f"{marker}🏘️  休憩所\n"
            else:
                result += f"{marker}🛍️  ショップ\n"
        
        result += "\n"
    
    return result


# ===== テスト用 =====

if __name__ == "__main__":
    # ツリー生成テスト
    nodes, root_id = generate_floor_tree(seed=42)
    
    print(f"Generated {len(nodes)} nodes")
    print(f"Root: {root_id}\n")
    
    # ツリー構造を表示
    for floor in range(1, 11):
        floor_nodes = [n for n in nodes.values() if n.floor_level == floor]
        print(f"Floor {floor}: {len(floor_nodes)} nodes")
        for node in sorted(floor_nodes, key=lambda x: int(x.node_id.split('_')[-1])):
            print(f"  {node.node_id}: type={node.node_type}, difficulty={node.difficulty}")
    
    # ツリー移動テスト
    current = nodes[root_id]
    print(f"\nStarting at: {current.node_id} ({current.node_type})")
    
    for _ in range(3):
        left, right = get_node_children(nodes, current.node_id)
        if left or right:
            print(f"Choices:")
            if left:
                print(f"  L: {left.node_id} ({left.node_type})")
            if right:
                print(f"  R: {right.node_id} ({right.node_type})")
            
            # ランダムに選択
            choice = random.choice([left, right])
            current = choice
            print(f"Selected: {current.node_id}\n")