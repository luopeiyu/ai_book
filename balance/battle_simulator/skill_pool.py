
from typing import Optional
from skill import Skill, NormalAttack, ViolentStrike, Charge, AdvancedCharge, SuperCharge, Poison, BigPoison, GroupAttack, SplashAttack, Heal, Revive, Stun, Invisibility, Armor, SpeedBoost, Recruit, Betray, Mine

# 技能配置数据
SKILL_POOL = {
    0: NormalAttack,      # 普通攻击：基础物理攻击，无冷却，伤害倍数1.0
    1: ViolentStrike,     # 暴力一击：每2次使用造成双倍伤害，其他次数miss，无冷却
    2: Charge,            # 蓄力：本回合不攻击，下回合伤害翻倍，无冷却
    3: AdvancedCharge,    # 高级蓄力：本回合不攻击，下2回合攻击力翻倍，冷却1回合
    4: SuperCharge,       # 超级蓄力：下个回合攻击2次，冷却2回合
    5: Poison,            # 毒药：连续2回合，每回合扣除100点血，无冷却
    6: BigPoison,         # 大毒药：连续3回合，每回合扣除30%血量，冷却1回合
    7: GroupAttack,       # 群体攻击：攻击敌方全体存活英雄，冷却1回合
    8: SplashAttack,      # 溅射攻击：主目标完整伤害，相邻敌人一半伤害，无冷却
    9: Heal,              # 治疗：恢复血量 = (施法者攻击力 + 受治疗者防御力) / 2，无冷却
    10: Revive,           # 复活：复活死亡英雄，恢复50%生命值，冷却2回合
    11: Stun,             # 眩晕：每3次使用成功眩晕敌人一次，无冷却
    12: Invisibility,     # 隐身：目标隐身2回合，无法被技能影响，冷却2回合
    13: Armor,            # 护甲：防御力1.5倍，可承受2次伤害，冷却1回合
    14: SpeedBoost,       # 速度提升：速度翻倍，持续2次行动，冷却2回合
    15: Recruit,          # 笼络：每3次使用成功笼络敌方角色一次，冷却1回合
    16: Betray,           # 背叛：每5次使用成功背叛一次，冷却1回合
    17: Mine,             # 地雷：2回合后引爆，所在阵营全体扣血50%，冷却2回合
}


def create_skill_instance(skill_id: int) -> Optional[Skill]:
    """创建技能实例"""
    if skill_id not in SKILL_POOL:
        return None
    
    skill_class = SKILL_POOL[skill_id]
    return skill_class()