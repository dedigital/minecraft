package com.example;

import com.example.gui.HudOverlay;
import com.example.modules.ModuleManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.KeyMapping;
import com.mojang.blaze3d.platform.InputConstants;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MCHelperClient implements ClientModInitializer {

    public static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    public static ModuleManager moduleManager;

    private static KeyMapping xrayKey;
    private static KeyMapping espKey;
    private static KeyMapping fullbrightKey;
    private static KeyMapping hudKey;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Mod yukleniyor...");

        moduleManager = new ModuleManager();

        xrayKey = KeyBindingHelper.registerKeyBinding(new KeyMapping(
                "X-Ray Toggle", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_F2, "MC Helper"
        ));
        espKey = KeyBindingHelper.registerKeyBinding(new KeyMapping(
                "ESP Toggle", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_F3, "MC Helper"
        ));
        fullbrightKey = KeyBindingHelper.registerKeyBinding(new KeyMapping(
                "Fullbright Toggle", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_F4, "MC Helper"
        ));
        hudKey = KeyBindingHelper.registerKeyBinding(new KeyMapping(
                "HUD Toggle", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_F6, "MC Helper"
        ));

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (xrayKey.consumeClick()) {
                moduleManager.toggle("xray");
            }
            while (espKey.consumeClick()) {
                moduleManager.toggle("esp");
            }
            while (fullbrightKey.consumeClick()) {
                moduleManager.toggle("fullbright");
                // Fullbright: set gamma to max or normal
                if (moduleManager.isEnabled("fullbright")) {
                    client.options.gamma().set(16.0);
                } else {
                    client.options.gamma().set(1.0);
                }
            }
            while (hudKey.consumeClick()) {
                moduleManager.toggle("hud");
            }
        });

        HudRenderCallback.EVENT.register((guiGraphics, deltaTracker) -> {
            if (moduleManager.isEnabled("hud")) {
                HudOverlay.render(guiGraphics, moduleManager);
            }
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
    }
}
