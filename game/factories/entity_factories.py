from game.components import consumable, equippable
from game.components.ai import HostileEnemy
from game.components.equipment import Equipment
from game.components.fighter import Fighter
from game.components.inventory import Inventory
from game.components.stats import Stats
from game.components.attachments import Attachments
import game.factories.limb_factories as limbs
from game.entity import Actor, Item

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(consume_time=25, number_of_turns=10),
    count=1,
    stackable=True,
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(consume_time=25, damage=12, radius=3),
    count=1,
    stackable=True,
)
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(consume_time=25, amount=4),
    count=1,
    stackable=True,
)
lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(consume_time=25, damage=20, maximum_range=5),
    count=1,
    stackable=True,
)

dagger = Item(
    char="/",
    color=(0, 191, 255),
    name="Dagger",
    equippable=equippable.Dagger(),
    stackable= False,
    )

sword = Item(
    char="/", 
    color=(0, 191, 255), 
    name="Sword", 
    equippable=equippable.Sword(),
    stackable= False,
    )

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
    stackable=False,
)

chain_mail = Item(char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail())
