package com.example;

import com.example.modules.ModuleManager;
import com.example.gui.HudOverlay;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MCHelperMod implements ClientModInitializer {

    public static final String MOD_ID = "mchelper";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    private static KeyBinding xrayKey;
    private static KeyBinding espKey;
    private static KeyBinding fullbrightKey;
    private static KeyBinding hudKey;

    public static ModuleManager moduleManager;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Mod yukleniyor...");

        moduleManager = new ModuleManager();

        xrayKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "X-Ray Toggle", InputUtil.Type.KEYSYM, GLFW.GLFW_KEY_F2, "MC Helper"
        ));
        espKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "ESP Toggle", InputUtil.Type.KEYSYM, GLFW.GLFW_KEY_F3, "MC Helper"
        ));
        fullbrightKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "Fullbright Toggle", InputUtil.Type.KEYSYM, GLFW.GLFW_KEY_F4, "MC Helper"
        ));
        hudKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "HUD Toggle", InputUtil.Type.KEYSYM, GLFW.GLFW_KEY_F6, "MC Helper"
        ));

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (xrayKey.wasPressed()) {
                moduleManager.toggle("xray");
            }
            while (espKey.wasPressed()) {
                moduleManager.toggle("esp");
            }
            while (fullbrightKey.wasPressed()) {
                moduleManager.toggle("fullbright");
            }
            while (hudKey.wasPressed()) {
                moduleManager.toggle("hud");
            }
        });

        HudRenderCallback.EVENT.register((drawContext, renderTickCounter) -> {
            if (moduleManager.isEnabled("hud")) {
                HudOverlay.render(drawContext, moduleManager);
            }
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
    }
}
