package com.example;

import com.example.modules.ModuleManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MCHelperClient implements ClientModInitializer {

    public static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    public static ModuleManager moduleManager;

    private boolean rWasDown = false;
    private boolean gWasDown = false;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Mod yukleniyor...");

        moduleManager = new ModuleManager();

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            // Don't process keys if a screen/chat is open
            if (client.screen != null) return;

            long window = GLFW.glfwGetCurrentContext();
            if (window == 0L) return;

            // R - X-Ray
            boolean rDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_R) == GLFW.GLFW_PRESS;
            if (rDown && !rWasDown) {
                moduleManager.toggle("xray");
                LOGGER.info("[MC Helper] X-Ray {}", moduleManager.isEnabled("xray") ? "ACILDI" : "KAPANDI");
                if (client.levelRenderer != null) {
                    client.levelRenderer.allChanged();
                }
            }
            rWasDown = rDown;

            // G - Fullbright
            boolean gDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_G) == GLFW.GLFW_PRESS;
            if (gDown && !gWasDown) {
                moduleManager.toggle("fullbright");
                LOGGER.info("[MC Helper] Fullbright {}", moduleManager.isEnabled("fullbright") ? "ACILDI" : "KAPANDI");
                if (moduleManager.isEnabled("fullbright")) {
                    client.options.gamma().set(16.0);
                } else {
                    client.options.gamma().set(1.0);
                }
            }
            gWasDown = gDown;
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
    }
}
