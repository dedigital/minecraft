package com.example;

import com.example.modules.ModuleManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class MCHelperClient implements ClientModInitializer {

    public static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    public static ModuleManager moduleManager;

    // Key toggle states
    private boolean gWasDown = false;
    private boolean hWasDown = false;
    private boolean jWasDown = false;
    private boolean kWasDown = false;
    private boolean nWasDown = false;
    private boolean mWasDown = false;
    private boolean rWasDown = false;
    private boolean bWasDown = false;
    private boolean vWasDown = false;
    private boolean pWasDown = false;

    // Zoom state
    private float originalFov = 70f;
    private boolean zooming = false;

    // Fullbright tracking
    private double lastGamma = 1.0;

    // Step assist tracking
    private double originalStepHeight = 0.6;
    private boolean stepApplied = false;

    // Info tick counter
    private int tickCounter = 0;

    // Remote control
    private static final int PORT = 25567;
    private final ConcurrentLinkedQueue<String> commandQueue = new ConcurrentLinkedQueue<>();
    private PrintWriter remoteOut;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Loading MC Helper v2.0...");

        moduleManager = new ModuleManager();
        startRemoteServer();

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            if (client.player == null || client.level == null) return;

            // Process remote commands
            String cmd;
            while ((cmd = commandQueue.poll()) != null) {
                processRemoteCommand(cmd, client);
            }

            long window = GLFW.glfwGetCurrentContext();
            if (window == 0L) return;

            boolean screenOpen = client.screen != null;

            // M - Open GUI
            boolean mDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_M) == GLFW.GLFW_PRESS;
            if (mDown && !mWasDown && !screenOpen) {
                client.setScreen(new MCHelperScreen(moduleManager));
            }
            mWasDown = mDown;

            if (!screenOpen) {
                handleKeyToggles(client, window);
            }

            // --- APPLY MODULE EFFECTS EVERY TICK ---

            applyFullbright(client);
            applyFlyTick(client);
            applySpeed(client);
            applyAutoSprint(client);
            applyNoFall(client);
            applyKillAura(client);
            applyAntiKnockback(client);
            applyStepAssist(client);
            applyNoHunger(client);

            // Send INFO to remote every 10 ticks
            tickCounter++;
            if (tickCounter >= 10) {
                tickCounter = 0;
                sendInfo(client);
            }
        });

        LOGGER.info("[MC Helper] MC Helper v2.0 loaded!");
        LOGGER.info("[MC Helper] Remote control port: " + PORT);
    }

    // ========== KEY HANDLING ==========

    private void handleKeyToggles(Minecraft client, long window) {
        // G - Fullbright
        boolean gDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_G) == GLFW.GLFW_PRESS;
        if (gDown && !gWasDown) {
            moduleManager.toggle("fullbright");
            sendStatus();
        }
        gWasDown = gDown;

        // H - Fly
        boolean hDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_H) == GLFW.GLFW_PRESS;
        if (hDown && !hWasDown) {
            moduleManager.toggle("fly");
            applyFlyImmediate(client);
            sendStatus();
        }
        hWasDown = hDown;

        // J - Speed
        boolean jDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_J) == GLFW.GLFW_PRESS;
        if (jDown && !jWasDown) {
            moduleManager.toggle("speed");
            sendStatus();
        }
        jWasDown = jDown;

        // K - Auto-Sprint
        boolean kDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_K) == GLFW.GLFW_PRESS;
        if (kDown && !kWasDown) {
            moduleManager.toggle("autosprint");
            sendStatus();
        }
        kWasDown = kDown;

        // N - No Fall
        boolean nDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_N) == GLFW.GLFW_PRESS;
        if (nDown && !nWasDown) {
            moduleManager.toggle("nofall");
            sendStatus();
        }
        nWasDown = nDown;

        // R - Kill Aura
        boolean rDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_R) == GLFW.GLFW_PRESS;
        if (rDown && !rWasDown) {
            moduleManager.toggle("killaura");
            sendStatus();
        }
        rWasDown = rDown;

        // B - Anti-Knockback
        boolean bDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_B) == GLFW.GLFW_PRESS;
        if (bDown && !bWasDown) {
            moduleManager.toggle("antiknockback");
            sendStatus();
        }
        bWasDown = bDown;

        // V - Step Assist
        boolean vDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_V) == GLFW.GLFW_PRESS;
        if (vDown && !vWasDown) {
            moduleManager.toggle("step");
            if (!moduleManager.isEnabled("step")) {
                resetStepHeight(client);
            }
            sendStatus();
        }
        vWasDown = vDown;

        // P - No Hunger
        boolean pDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_P) == GLFW.GLFW_PRESS;
        if (pDown && !pWasDown) {
            moduleManager.toggle("nohunger");
            sendStatus();
        }
        pWasDown = pDown;

        // C - Zoom (hold, not toggle)
        boolean cDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_C) == GLFW.GLFW_PRESS;
        if (cDown && !zooming) {
            zooming = true;
            originalFov = client.options.fov().get().floatValue();
            client.options.fov().set(moduleManager.getZoomFov());
        } else if (!cDown && zooming) {
            zooming = false;
            client.options.fov().set((int) originalFov);
        } else if (cDown && zooming) {
            // Update FOV if zoom config changed while held
            client.options.fov().set(moduleManager.getZoomFov());
        }
    }

    // ========== MODULE EFFECTS ==========

    private void applyFullbright(Minecraft client) {
        double targetGamma = moduleManager.isEnabled("fullbright") ? 16.0 : 1.0;
        if (lastGamma != targetGamma) {
            client.options.gamma().set(targetGamma);
            lastGamma = targetGamma;
        }
    }

    private void applyFlyImmediate(Minecraft client) {
        if (client.player != null) {
            boolean enabled = moduleManager.isEnabled("fly");
            client.player.getAbilities().mayfly = enabled;
            client.player.getAbilities().flying = enabled;
            client.player.onUpdateAbilities();
        }
    }

    private void applyFlyTick(Minecraft client) {
        if (moduleManager.isEnabled("fly")) {
            if (!client.player.getAbilities().mayfly) {
                client.player.getAbilities().mayfly = true;
                client.player.getAbilities().flying = true;
                client.player.onUpdateAbilities();
            }
        }
    }

    private void applySpeed(Minecraft client) {
        if (moduleManager.isEnabled("speed") && client.player.onGround()) {
            double mult = moduleManager.getSpeedMult();
            Vec3 vel = client.player.getDeltaMovement();
            client.player.setDeltaMovement(vel.x * mult, vel.y, vel.z * mult);
        }
    }

    private void applyAutoSprint(Minecraft client) {
        if (moduleManager.isEnabled("autosprint")) {
            if (client.player.input.getMoveVector().length() > 0) {
                client.player.setSprinting(true);
            }
        }
    }

    private void applyNoFall(Minecraft client) {
        if (moduleManager.isEnabled("nofall")) {
            client.player.fallDistance = 0.0f;
            if (client.getSingleplayerServer() != null) {
                ServerPlayer serverPlayer = client.getSingleplayerServer()
                        .getPlayerList().getPlayer(client.player.getUUID());
                if (serverPlayer != null) {
                    serverPlayer.fallDistance = 0.0f;
                }
            }
        }
    }

    private void applyKillAura(Minecraft client) {
        if (!moduleManager.isEnabled("killaura")) return;
        if (client.gameMode == null) return;

        // Only attack when attack strength is full (cooldown ready)
        if (client.player.getAttackStrengthScale(0.0f) < 1.0f) return;

        double range = moduleManager.getAuraRange();
        AABB searchBox = client.player.getBoundingBox().inflate(range);

        List<LivingEntity> entities = client.level.getEntitiesOfClass(
                LivingEntity.class,
                searchBox,
                e -> e instanceof Monster && e.isAlive() && e != client.player
        );

        if (!entities.isEmpty()) {
            // Sort by distance and attack nearest
            entities.sort(Comparator.comparingDouble(e -> e.distanceToSqr(client.player)));
            LivingEntity target = entities.get(0);

            // Double check range (bounding box inflate can be slightly larger)
            if (client.player.distanceTo(target) <= range) {
                client.gameMode.attack(client.player, target);
                client.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            }
        }
    }

    private void applyAntiKnockback(Minecraft client) {
        if (!moduleManager.isEnabled("antiknockback")) return;
        if (client.player.hurtTime > 0) {
            Vec3 vel = client.player.getDeltaMovement();
            client.player.setDeltaMovement(vel.x * 0.1, vel.y, vel.z * 0.1);
        }
    }

    private void applyStepAssist(Minecraft client) {
        if (moduleManager.isEnabled("step")) {
            try {
                var attr = client.player.getAttribute(
                        net.minecraft.world.entity.ai.attributes.Attributes.STEP_HEIGHT);
                if (attr != null) {
                    if (attr.getBaseValue() < 1.5) {
                        if (!stepApplied) {
                            originalStepHeight = attr.getBaseValue();
                        }
                        attr.setBaseValue(1.5);
                        stepApplied = true;
                    }
                }
            } catch (Throwable t) {
                // Attributes.STEP_HEIGHT may not exist on this version
                // Fallback: boost Y velocity when colliding horizontally
                if (client.player.horizontalCollision && client.player.onGround()) {
                    Vec3 vel = client.player.getDeltaMovement();
                    client.player.setDeltaMovement(vel.x, 0.42, vel.z);
                }
            }
        }
    }

    private void resetStepHeight(Minecraft client) {
        if (stepApplied && client.player != null) {
            try {
                var attr = client.player.getAttribute(
                        net.minecraft.world.entity.ai.attributes.Attributes.STEP_HEIGHT);
                if (attr != null) {
                    attr.setBaseValue(originalStepHeight);
                }
            } catch (Throwable t) {
                // Ignore if attribute doesn't exist
            }
            stepApplied = false;
        }
    }

    private void applyNoHunger(Minecraft client) {
        if (!moduleManager.isEnabled("nohunger")) return;
        if (client.getSingleplayerServer() != null) {
            ServerPlayer serverPlayer = client.getSingleplayerServer()
                    .getPlayerList().getPlayer(client.player.getUUID());
            if (serverPlayer != null) {
                serverPlayer.getFoodData().setFoodLevel(20);
                serverPlayer.getFoodData().setSaturationLevel(20.0f);
            }
        }
    }

    // ========== REMOTE CONTROL ==========

    private void processRemoteCommand(String cmd, Minecraft client) {
        String[] parts = cmd.trim().split("\\s+");
        if (parts.length == 0) return;

        String action = parts[0].toLowerCase();

        if (action.equals("status")) {
            sendStatus();
            return;
        }

        if (action.equals("set") && parts.length >= 3) {
            processSetCommand(parts[1].toLowerCase(), parts[2]);
            return;
        }

        if (parts.length < 2) return;
        String module = parts[1].toLowerCase();

        switch (action) {
            case "toggle":
                moduleManager.toggle(module);
                if (module.equals("fly")) applyFlyImmediate(client);
                if (module.equals("step") && !moduleManager.isEnabled("step")) resetStepHeight(client);
                LOGGER.info("[MC Helper] Remote toggle: {} -> {}", module, moduleManager.isEnabled(module));
                sendStatus();
                break;
            case "enable":
                if (!moduleManager.isEnabled(module)) {
                    moduleManager.toggle(module);
                    if (module.equals("fly")) applyFlyImmediate(client);
                }
                sendStatus();
                break;
            case "disable":
                if (moduleManager.isEnabled(module)) {
                    moduleManager.toggle(module);
                    if (module.equals("fly")) applyFlyImmediate(client);
                    if (module.equals("step")) resetStepHeight(client);
                }
                sendStatus();
                break;
        }
    }

    private void processSetCommand(String key, String value) {
        try {
            switch (key) {
                case "speed_mult":
                    moduleManager.setSpeedMult(Double.parseDouble(value));
                    LOGGER.info("[MC Helper] speed_mult set to {}", value);
                    break;
                case "zoom_fov":
                    moduleManager.setZoomFov(Integer.parseInt(value));
                    LOGGER.info("[MC Helper] zoom_fov set to {}", value);
                    break;
                case "aura_range":
                    moduleManager.setAuraRange(Double.parseDouble(value));
                    LOGGER.info("[MC Helper] aura_range set to {}", value);
                    break;
                default:
                    LOGGER.warn("[MC Helper] Unknown config key: {}", key);
                    return;
            }
            sendConfig();
        } catch (NumberFormatException e) {
            LOGGER.warn("[MC Helper] Invalid value for {}: {}", key, value);
        }
    }

    private void sendStatus() {
        if (remoteOut != null) {
            StringBuilder sb = new StringBuilder("STATUS ");
            boolean first = true;
            for (var entry : moduleManager.getModules().entrySet()) {
                if (!first) sb.append(",");
                sb.append(entry.getKey()).append("=").append(entry.getValue().isEnabled() ? "1" : "0");
                first = false;
            }
            remoteOut.println(sb.toString());
            remoteOut.flush();
        }
    }

    private void sendInfo(Minecraft client) {
        if (remoteOut == null || client.player == null) return;
        try {
            double x = Math.round(client.player.getX() * 10.0) / 10.0;
            double y = Math.round(client.player.getY() * 10.0) / 10.0;
            double z = Math.round(client.player.getZ() * 10.0) / 10.0;
            float hp = client.player.getHealth();
            float maxHp = client.player.getMaxHealth();
            int food = client.player.getFoodData().getFoodLevel();
            int armor = client.player.getArmorValue();
            int fps = client.getFps();

            String info = String.format("INFO x=%.1f,y=%.1f,z=%.1f,hp=%.1f,maxhp=%.1f,food=%d,armor=%d,fps=%d",
                    x, y, z, hp, maxHp, food, armor, fps);
            remoteOut.println(info);
            remoteOut.flush();
        } catch (Exception e) {
            // Ignore errors in info sending
        }
    }

    private void sendConfig() {
        if (remoteOut != null) {
            String config = String.format("CONFIG speed_mult=%.1f,zoom_fov=%d,aura_range=%.1f",
                    moduleManager.getSpeedMult(), moduleManager.getZoomFov(), moduleManager.getAuraRange());
            remoteOut.println(config);
            remoteOut.flush();
        }
    }

    private void startRemoteServer() {
        Thread serverThread = new Thread(() -> {
            try (ServerSocket serverSocket = new ServerSocket(PORT)) {
                serverSocket.setReuseAddress(true);
                LOGGER.info("[MC Helper] Remote server started on port {}", PORT);
                while (true) {
                    try {
                        Socket socket = serverSocket.accept();
                        LOGGER.info("[MC Helper] Remote client connected");
                        remoteOut = new PrintWriter(socket.getOutputStream(), true);
                        BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                        remoteOut.println("CONNECTED MC Helper v2.0");
                        sendStatus();
                        sendConfig();

                        String line;
                        while ((line = in.readLine()) != null) {
                            commandQueue.add(line);
                        }
                        LOGGER.info("[MC Helper] Remote client disconnected");
                        remoteOut = null;
                    } catch (Exception e) {
                        LOGGER.warn("[MC Helper] Remote client error: {}", e.getMessage());
                        remoteOut = null;
                    }
                }
            } catch (Exception e) {
                LOGGER.error("[MC Helper] Remote server failed: {}", e.getMessage());
            }
        }, "MCHelper-Remote");
        serverThread.setDaemon(true);
        serverThread.start();
    }
}
