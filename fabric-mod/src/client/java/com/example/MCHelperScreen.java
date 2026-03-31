package com.example;

import com.example.modules.Module;
import com.example.modules.ModuleManager;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

import java.util.Map;

public class MCHelperScreen extends Screen {

    private final ModuleManager moduleManager;

    public MCHelperScreen(ModuleManager moduleManager) {
        super(Component.literal("MC Helper"));
        this.moduleManager = moduleManager;
    }

    @Override
    protected void init() {
        int centerX = this.width / 2;
        int startY = 50;
        int buttonWidth = 200;
        int buttonHeight = 20;
        int spacing = 25;

        int i = 0;
        for (Map.Entry<String, Module> entry : moduleManager.getModules().entrySet()) {
            String id = entry.getKey();
            Module module = entry.getValue();

            int y = startY + (i * spacing);
            String label = module.getName() + " [" + module.getKey() + "] - " +
                    (module.isEnabled() ? "ACIK" : "KAPALI");

            this.addRenderableWidget(Button.builder(
                    Component.literal(label),
                    button -> {
                        moduleManager.toggle(id);

                        // Handle xray - force chunk rebuild
                        if (id.equals("xray") && minecraft != null && minecraft.levelRenderer != null) {
                            minecraft.levelRenderer.allChanged();
                        }

                        // Handle fullbright gamma
                        if (id.equals("fullbright") && minecraft != null) {
                            if (moduleManager.isEnabled("fullbright")) {
                                minecraft.options.gamma().set(16.0);
                            } else {
                                minecraft.options.gamma().set(1.0);
                            }
                        }

                        // Handle fly
                        if (id.equals("fly") && minecraft != null && minecraft.player != null) {
                            minecraft.player.getAbilities().mayfly = moduleManager.isEnabled("fly");
                            minecraft.player.getAbilities().flying = moduleManager.isEnabled("fly");
                            minecraft.player.onUpdateAbilities();
                        }

                        // Refresh screen
                        this.rebuildWidgets();
                    }
            ).bounds(centerX - buttonWidth / 2, y, buttonWidth, buttonHeight).build());

            i++;
        }

        // Zoom info
        int infoY = startY + (i * spacing) + 10;
        this.addRenderableWidget(Button.builder(
                Component.literal("Zoom [C] - Basili tut"),
                button -> {}
        ).bounds(centerX - buttonWidth / 2, infoY, buttonWidth, buttonHeight).build());

        // Close button
        this.addRenderableWidget(Button.builder(
                Component.literal("Kapat [ESC]"),
                button -> this.onClose()
        ).bounds(centerX - buttonWidth / 2, this.height - 40, buttonWidth, buttonHeight).build());
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        // Dark background
        graphics.fill(0, 0, this.width, this.height, 0x88000000);

        // Title
        graphics.drawCenteredString(this.font, "MC Helper - Hile Menusu", this.width / 2, 20, 0x55FF55);

        // Render buttons
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
