package com.example;

import com.example.modules.Module;
import com.example.modules.ModuleManager;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class MCHelperScreen extends Screen {

    private final ModuleManager moduleManager;

    private static final String[] CATEGORY_ORDER = {"combat", "movement", "visual", "player"};
    private static final Map<String, String> CATEGORY_LABELS = new LinkedHashMap<>();

    static {
        CATEGORY_LABELS.put("combat", "--- Combat ---");
        CATEGORY_LABELS.put("movement", "--- Movement ---");
        CATEGORY_LABELS.put("visual", "--- Visual ---");
        CATEGORY_LABELS.put("player", "--- Player ---");
    }

    public MCHelperScreen(ModuleManager moduleManager) {
        super(Component.literal("MC Helper v2.0"));
        this.moduleManager = moduleManager;
    }

    @Override
    protected void init() {
        int centerX = this.width / 2;
        int startY = 30;
        int buttonWidth = 220;
        int buttonHeight = 20;
        int spacing = 24;
        int headerSpacing = 18;

        int y = startY;

        // Title is handled by Screen itself, start with categories
        for (String category : CATEGORY_ORDER) {
            // Collect modules in this category
            List<Map.Entry<String, Module>> categoryModules = new ArrayList<>();
            for (Map.Entry<String, Module> entry : moduleManager.getModules().entrySet()) {
                if (entry.getValue().getCategory().equals(category)) {
                    categoryModules.add(entry);
                }
            }

            if (categoryModules.isEmpty()) continue;

            // Category header (non-interactive button)
            this.addRenderableWidget(Button.builder(
                    Component.literal(CATEGORY_LABELS.get(category)),
                    button -> {}
            ).bounds(centerX - buttonWidth / 2, y, buttonWidth, buttonHeight).build());
            y += headerSpacing;

            // Module buttons
            for (Map.Entry<String, Module> entry : categoryModules) {
                String id = entry.getKey();
                Module module = entry.getValue();

                String label = module.getName() + " [" + module.getKey() + "] - " +
                        (module.isEnabled() ? "ON" : "OFF");

                int btnY = y;
                this.addRenderableWidget(Button.builder(
                        Component.literal(label),
                        button -> {
                            moduleManager.toggle(id);

                            // Handle fly toggle
                            if (id.equals("fly") && minecraft != null && minecraft.player != null) {
                                minecraft.player.getAbilities().mayfly = moduleManager.isEnabled("fly");
                                minecraft.player.getAbilities().flying = moduleManager.isEnabled("fly");
                                minecraft.player.onUpdateAbilities();
                            }

                            // Handle fullbright toggle
                            if (id.equals("fullbright") && minecraft != null) {
                                if (moduleManager.isEnabled("fullbright")) {
                                    minecraft.options.gamma().set(16.0);
                                } else {
                                    minecraft.options.gamma().set(1.0);
                                }
                            }

                            // Refresh screen to update labels
                            this.rebuildWidgets();
                        }
                ).bounds(centerX - buttonWidth / 2, btnY, buttonWidth, buttonHeight).build());
                y += spacing;
            }

            y += 4; // Extra gap between categories
        }

        // Zoom info (hold-based, not toggleable)
        this.addRenderableWidget(Button.builder(
                Component.literal("Zoom [C] - Hold to zoom (FOV: " + moduleManager.getZoomFov() + ")"),
                button -> {}
        ).bounds(centerX - buttonWidth / 2, y, buttonWidth, buttonHeight).build());
        y += spacing;

        // Config display
        y += 4;
        String configText = String.format("Speed: %.1fx | Aura Range: %.1f | Zoom FOV: %d",
                moduleManager.getSpeedMult(), moduleManager.getAuraRange(), moduleManager.getZoomFov());
        this.addRenderableWidget(Button.builder(
                Component.literal(configText),
                button -> {}
        ).bounds(centerX - buttonWidth / 2, y, buttonWidth, buttonHeight).build());
        y += spacing;

        // Close button at bottom
        this.addRenderableWidget(Button.builder(
                Component.literal("Close [ESC]"),
                button -> this.onClose()
        ).bounds(centerX - buttonWidth / 2, this.height - 30, buttonWidth, buttonHeight).build());
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
