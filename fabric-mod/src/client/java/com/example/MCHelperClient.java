package com.example;

import com.example.modules.Module;
import com.example.modules.ModuleManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.Minecraft;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;

public class MCHelperClient implements ClientModInitializer {

    public static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    public static ModuleManager moduleManager;

    // Key states
    private boolean xWasDown = false;   // X-Ray
    private boolean gWasDown = false;   // Fullbright
    private boolean hWasDown = false;   // Fly
    private boolean jWasDown = false;   // Speed
    private boolean kWasDown = false;   // Auto-Sprint
    private boolean nWasDown = false;   // No Fall
    private boolean mWasDown = false;   // GUI Menu
    private boolean cWasDown = false;   // Zoom

    private float originalFov = 70f;
    private boolean zooming = false;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Mod yukleniyor...");

        moduleManager = new ModuleManager();

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            if (client.player == null) return;

            long window = GLFW.glfwGetCurrentContext();
            if (window == 0L) return;

            boolean screenOpen = client.screen != null;

            // M - Open GUI (works even with screen open)
            boolean mDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_M) == GLFW.GLFW_PRESS;
            if (mDown && !mWasDown && !screenOpen) {
                client.setScreen(new MCHelperScreen(moduleManager));
            }
            mWasDown = mDown;

            // Don't process other keys if screen is open
            if (screenOpen) return;

            // X - X-Ray
            boolean xDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_X) == GLFW.GLFW_PRESS;
            if (xDown && !xWasDown) {
                moduleManager.toggle("xray");
                // Force chunk rebuild to apply X-Ray
                if (client.levelRenderer != null) {
                    client.levelRenderer.allChanged();
                }
            }
            xWasDown = xDown;

            // G - Fullbright
            boolean gDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_G) == GLFW.GLFW_PRESS;
            if (gDown && !gWasDown) {
                moduleManager.toggle("fullbright");
                if (moduleManager.isEnabled("fullbright")) {
                    client.options.gamma().set(16.0);
                } else {
                    client.options.gamma().set(1.0);
                }
            }
            gWasDown = gDown;

            // H - Fly
            boolean hDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_H) == GLFW.GLFW_PRESS;
            if (hDown && !hWasDown) {
                moduleManager.toggle("fly");
                if (client.player.getAbilities().mayfly || moduleManager.isEnabled("fly")) {
                    client.player.getAbilities().mayfly = moduleManager.isEnabled("fly");
                    client.player.getAbilities().flying = moduleManager.isEnabled("fly");
                    client.player.onUpdateAbilities();
                }
            }
            hWasDown = hDown;

            // J - Speed Boost
            boolean jDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_J) == GLFW.GLFW_PRESS;
            if (jDown && !jWasDown) {
                moduleManager.toggle("speed");
            }
            jWasDown = jDown;

            // Apply speed
            if (moduleManager.isEnabled("speed")) {
                client.player.getAbilities().setWalkingSpeed(0.2f); // 2x normal
                client.player.getAbilities().setFlyingSpeed(0.1f);  // 5x normal
            } else {
                client.player.getAbilities().setWalkingSpeed(0.1f); // normal
                client.player.getAbilities().setFlyingSpeed(0.02f); // normal
            }

            // K - Auto-Sprint
            boolean kDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_K) == GLFW.GLFW_PRESS;
            if (kDown && !kWasDown) {
                moduleManager.toggle("autosprint");
            }
            kWasDown = kDown;

            // Apply auto-sprint
            if (moduleManager.isEnabled("autosprint") && client.player.input.getMoveVector().length() > 0) {
                client.player.setSprinting(true);
            }

            // N - No Fall Damage
            boolean nDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_N) == GLFW.GLFW_PRESS;
            if (nDown && !nWasDown) {
                moduleManager.toggle("nofall");
            }
            nWasDown = nDown;

            // Apply no fall
            if (moduleManager.isEnabled("nofall")) {
                client.player.resetFallDistance();
            }

            // C - Zoom (hold)
            boolean cDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_C) == GLFW.GLFW_PRESS;
            if (cDown && !zooming) {
                zooming = true;
                originalFov = client.options.fov().get().floatValue();
                client.options.fov().set(20); // Zoom in
            } else if (!cDown && zooming) {
                zooming = false;
                client.options.fov().set((int) originalFov);
            }
        });

        // HUD Overlay - show active modules on screen
        HudRenderCallback.EVENT.register((graphics, delta) -> {
            Minecraft client = Minecraft.getInstance();
            if (client.player == null) return;
            if (client.screen != null) return; // Don't show when GUI is open

            int y = 5;
            // Title
            graphics.drawString(client.font, "[MC Helper]", 5, y, 0x55FF55);
            y += 12;

            boolean anyActive = false;
            for (Map.Entry<String, Module> entry : moduleManager.getModules().entrySet()) {
                Module module = entry.getValue();
                if (module.isEnabled()) {
                    graphics.drawString(client.font, module.getName() + " [" + module.getKey() + "]", 5, y, 0xFFFFFF);
                    y += 10;
                    anyActive = true;
                }
            }

            if (zooming) {
                graphics.drawString(client.font, "Zoom [C]", 5, y, 0xFFFFFF);
                y += 10;
                anyActive = true;
            }

            if (!anyActive) {
                graphics.drawString(client.font, "M = Menu", 5, y, 0x888888);
            }
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
        LOGGER.info("[MC Helper] Tuslar: X=XRay G=Fullbright H=Fly J=Speed K=Sprint N=NoFall C=Zoom M=Menu");
    }
}
