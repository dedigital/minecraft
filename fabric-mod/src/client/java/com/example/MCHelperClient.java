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

    private boolean f2WasDown = false;
    private boolean f4WasDown = false;

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
                if (client.levelRenderer != null) {
                    client.levelRenderer.allChanged();
                }
            }
            f2WasDown = f2Down;

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
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
    }
}
