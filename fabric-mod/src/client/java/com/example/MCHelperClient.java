package com.example;

import com.example.gui.HudOverlay;
import com.example.modules.ModuleManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MCHelperClient implements ClientModInitializer {

    public static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    public static ModuleManager moduleManager;

    // Track previous key states to detect press (not hold)
    private boolean f2WasDown = false;
    private boolean f3WasDown = false;
    private boolean f4WasDown = false;
    private boolean f6WasDown = false;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Mod yukleniyor...");

        moduleManager = new ModuleManager();

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            long window = GLFW.glfwGetCurrentContext();
            if (window == 0L) return;

            // F2 - X-Ray
            boolean f2Down = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_F2) == GLFW.GLFW_PRESS;
            if (f2Down && !f2WasDown) {
                moduleManager.toggle("xray");
                // Force chunk rebuild for X-Ray
                if (client.levelRenderer != null) {
                    client.levelRenderer.allChanged();
                }
            }
            f2WasDown = f2Down;

            // F3 - ESP
            boolean f3Down = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_F3) == GLFW.GLFW_PRESS;
            if (f3Down && !f3WasDown) {
                moduleManager.toggle("esp");
            }
            f3WasDown = f3Down;

            // F4 - Fullbright
            boolean f4Down = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_F4) == GLFW.GLFW_PRESS;
            if (f4Down && !f4WasDown) {
                moduleManager.toggle("fullbright");
                if (moduleManager.isEnabled("fullbright")) {
                    client.options.gamma().set(16.0);
                } else {
                    client.options.gamma().set(1.0);
                }
            }
            f4WasDown = f4Down;

            // F6 - HUD
            boolean f6Down = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_F6) == GLFW.GLFW_PRESS;
            if (f6Down && !f6WasDown) {
                moduleManager.toggle("hud");
            }
            f6WasDown = f6Down;
        });

        HudRenderCallback.EVENT.register((guiGraphics, deltaTracker) -> {
            if (moduleManager.isEnabled("hud")) {
                HudOverlay.render(guiGraphics, moduleManager);
            }
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
    }
}
