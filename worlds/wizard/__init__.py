import asyncio

import wx

from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, components, Type, launch_subprocess
from .frame import WizardFrame


def launch_wizard():
    async def main():
        app = wx.App()
        frm = WizardFrame()
        frm.Show()
        app_task = asyncio.create_task(app.MainLoop())
        await app_task

    asyncio.run(main())


components.append(Component("YAML Wizard", None, func=launch_wizard, component_type=Type.TOOL))


class ApWizardWorld(World):
    item_name_to_id = {}
    location_name_to_id = {}
