package com.example.gui;

import com.example.modules.Module;
import com.example.modules.ModuleManager;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;

import java.util.Map;

public class HudOverlay {

    public static void render(GuiGraphics graphics, ModuleManager moduleManager) {
        Minecraft client = Minecraft.getInstance();
        if (client == null || client.player == null) return;

        Font font = client.font;
        int y = 5;
        int x = 5;

        // Title
        graphics.drawString(font, "MC Helper v1.0", x, y, 0x00FF41);
        y += 12;
        graphics.drawString(font, "================", x, y, 0x444444);
        y += 12;

        // Module statuses
        for (Map.Entry<String, Module> entry : moduleManager.getModules().entrySet()) {
            Module module = entry.getValue();
            String status = module.isEnabled() ? " ON" : " OFF";
            int color = module.isEnabled() ? 0x00FF00 : 0xFF4444;
            graphics.drawString(font, module.getName() + ":" + status, x, y, color);
            y += 11;
        }

        y += 5;
        graphics.drawString(font, "----------------", x, y, 0x444444);
        y += 12;

        // Coordinates
        BlockPos pos = client.player.blockPosition();
        graphics.drawString(font,
                String.format("XYZ: %d / %d / %d", pos.getX(), pos.getY(), pos.getZ()),
                x, y, 0x00CCFF);
        y += 11;

        // Direction
        String facing = getDirection(client.player.getYRot());
        graphics.drawString(font, "Yon: " + facing, x, y, 0x00CCFF);
        y += 11;

        // FPS
        graphics.drawString(font, "FPS: " + client.getFps(), x, y, 0xAAAAAA);
        y += 16;

        // Entity counter when ESP is on
        if (moduleManager.isEnabled("esp") && client.level != null) {
            graphics.drawString(font, "--- ESP ---", x, y, 0xFF00FF);
            y += 12;

            int hostile = 0, passive = 0, players = 0;
            for (Entity entity : client.level.entitiesForRendering()) {
                if (entity instanceof Monster) hostile++;
                else if (entity instanceof Animal) passive++;
                else if (entity instanceof Player && entity != client.player) players++;
            }

            graphics.drawString(font, "Dusman: " + hostile, x, y, 0xFF4444);
            y += 11;
            graphics.drawString(font, "Pasif: " + passive, x, y, 0x44FF44);
            y += 11;
            graphics.drawString(font, "Oyuncu: " + players, x, y, 0xFFFF00);
            y += 16;
        }

        // Health & Hunger
        graphics.drawString(font, "----------------", x, y, 0x444444);
        y += 12;

        float health = client.player.getHealth();
        int maxHealth = (int) client.player.getMaxHealth();
        int healthColor = health > 10 ? 0x00FF00 : (health > 5 ? 0xFFFF00 : 0xFF0000);
        graphics.drawString(font,
                String.format("Can: %.0f/%d", health, maxHealth), x, y, healthColor);
        y += 11;

        int food = client.player.getFoodData().getFoodLevel();
        int foodColor = food > 12 ? 0x00FF00 : (food > 6 ? 0xFFFF00 : 0xFF0000);
        graphics.drawString(font, "Aclik: " + food + "/20", x, y, foodColor);
        y += 11;

        graphics.drawString(font, "Zirh: " + client.player.getArmorValue(), x, y, 0xCCCCCC);
        y += 15;

        // Keybind hints
        graphics.drawString(font, "F2:XRay F3:ESP", x, y, 0x666666);
        y += 11;
        graphics.drawString(font, "F4:Bright F6:HUD", x, y, 0x666666);
    }

    private static String getDirection(float yaw) {
        yaw = ((yaw % 360) + 360) % 360;
        if (yaw >= 315 || yaw < 45) return "Guney (S)";
        if (yaw >= 45 && yaw < 135) return "Bati (W)";
        if (yaw >= 135 && yaw < 225) return "Kuzey (N)";
        return "Dogu (E)";
    }
}
