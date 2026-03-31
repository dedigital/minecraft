package com.example;

import com.example.modules.ModuleManager;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.server.level.ServerPlayer;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ConcurrentLinkedQueue;

public class MCHelperClient implements ClientModInitializer {

    public static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    public static ModuleManager moduleManager;

    private boolean gWasDown = false;
    private boolean hWasDown = false;
    private boolean jWasDown = false;
    private boolean kWasDown = false;
    private boolean nWasDown = false;
    private boolean mWasDown = false;

    private float originalFov = 70f;
    private boolean zooming = false;
    private double lastGamma = 1.0;

    // Remote control
    private static final int PORT = 25567;
    private final ConcurrentLinkedQueue<String> commandQueue = new ConcurrentLinkedQueue<>();
    private PrintWriter remoteOut;

    @Override
    public void onInitializeClient() {
        LOGGER.info("[MC Helper] Mod yukleniyor...");

        moduleManager = new ModuleManager();
        startRemoteServer();

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            if (client.player == null) return;

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

            if (screenOpen) return;

            // --- KEY TOGGLES ---

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
                applyFly(client);
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

            // C - Zoom (hold)
            boolean cDown = GLFW.glfwGetKey(window, GLFW.GLFW_KEY_C) == GLFW.GLFW_PRESS;
            if (cDown && !zooming) {
                zooming = true;
                originalFov = client.options.fov().get().floatValue();
                client.options.fov().set(20);
            } else if (!cDown && zooming) {
                zooming = false;
                client.options.fov().set((int) originalFov);
            }

            // --- APPLY EFFECTS EVERY TICK ---

            // Fullbright - apply gamma every tick
            double targetGamma = moduleManager.isEnabled("fullbright") ? 16.0 : 1.0;
            if (lastGamma != targetGamma) {
                client.options.gamma().set(targetGamma);
                lastGamma = targetGamma;
            }

            // Speed - multiply velocity
            if (moduleManager.isEnabled("speed") && client.player.onGround()) {
                var movement = client.player.getDeltaMovement();
                client.player.setDeltaMovement(movement.x * 1.8, movement.y, movement.z * 1.8);
            }

            // Auto-Sprint
            if (moduleManager.isEnabled("autosprint") && client.player.input.getMoveVector().length() > 0) {
                client.player.setSprinting(true);
            }

            // No Fall - reset on both client and server
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

            // Fly - keep abilities synced
            if (moduleManager.isEnabled("fly")) {
                if (!client.player.getAbilities().mayfly) {
                    client.player.getAbilities().mayfly = true;
                    client.player.onUpdateAbilities();
                }
            }
        });

        LOGGER.info("[MC Helper] Mod basariyla yuklendi!");
        LOGGER.info("[MC Helper] Remote kontrol portu: " + PORT);
    }

    private void applyFly(Minecraft client) {
        if (client.player != null) {
            client.player.getAbilities().mayfly = moduleManager.isEnabled("fly");
            client.player.getAbilities().flying = moduleManager.isEnabled("fly");
            client.player.onUpdateAbilities();
        }
    }

    private void processRemoteCommand(String cmd, Minecraft client) {
        String[] parts = cmd.trim().split(" ");
        if (parts.length < 2) {
            if (parts.length == 1 && parts[0].equals("status")) {
                sendStatus();
            }
            return;
        }

        String action = parts[0];
        String module = parts[1].toLowerCase();

        switch (action) {
            case "toggle":
                moduleManager.toggle(module);
                if (module.equals("fly")) applyFly(client);
                LOGGER.info("[MC Helper] Remote toggle: " + module + " -> " + moduleManager.isEnabled(module));
                sendStatus();
                break;
            case "enable":
                if (!moduleManager.isEnabled(module)) moduleManager.toggle(module);
                if (module.equals("fly")) applyFly(client);
                sendStatus();
                break;
            case "disable":
                if (moduleManager.isEnabled(module)) moduleManager.toggle(module);
                if (module.equals("fly")) applyFly(client);
                sendStatus();
                break;
        }
    }

    private void sendStatus() {
        if (remoteOut != null) {
            StringBuilder sb = new StringBuilder("STATUS ");
            moduleManager.getModules().forEach((id, module) ->
                sb.append(id).append("=").append(module.isEnabled() ? "1" : "0").append(",")
            );
            remoteOut.println(sb.toString().trim());
            remoteOut.flush();
        }
    }

    private void startRemoteServer() {
        Thread serverThread = new Thread(() -> {
            try (ServerSocket serverSocket = new ServerSocket(PORT)) {
                serverSocket.setReuseAddress(true);
                LOGGER.info("[MC Helper] Remote server started on port " + PORT);
                while (true) {
                    try {
                        Socket socket = serverSocket.accept();
                        LOGGER.info("[MC Helper] Remote client connected");
                        remoteOut = new PrintWriter(socket.getOutputStream(), true);
                        BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                        remoteOut.println("CONNECTED MC Helper v1.0");
                        sendStatus();
                        String line;
                        while ((line = in.readLine()) != null) {
                            commandQueue.add(line);
                        }
                        LOGGER.info("[MC Helper] Remote client disconnected");
                        remoteOut = null;
                    } catch (Exception e) {
                        LOGGER.warn("[MC Helper] Remote client error: " + e.getMessage());
                        remoteOut = null;
                    }
                }
            } catch (Exception e) {
                LOGGER.error("[MC Helper] Remote server failed: " + e.getMessage());
            }
        }, "MCHelper-Remote");
        serverThread.setDaemon(true);
        serverThread.start();
    }
}
