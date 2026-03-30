package com.example.gui;

import com.example.modules.Module;
import com.example.modules.ModuleManager;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.font.TextRenderer;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.entity.Entity;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.passive.AnimalEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.util.math.BlockPos;

import java.util.Map;

public class HudOverlay {

    public static void render(DrawContext context, ModuleManager moduleManager) {
        MinecraftClient client = MinecraftClient.getInstance();
        if (client == null || client.player == null) return;

        TextRenderer textRenderer = client.textRenderer;
        int y = 5;
        int x = 5;

        // Title
        context.drawTextWithShadow(textRenderer, "MC Helper v1.0", x, y, 0x00FF41);
        y += 12;
        context.drawTextWithShadow(textRenderer, "================", x, y, 0x444444);
        y += 12;

        // Module statuses
        for (Map.Entry<String, Module> entry : moduleManager.getModules().entrySet()) {
            Module module = entry.getValue();
            String status = module.isEnabled() ? " ON" : " OFF";
            int color = module.isEnabled() ? 0x00FF00 : 0xFF4444;
            context.drawTextWithShadow(textRenderer, module.getName() + ":" + status, x, y, color);
            y += 11;
        }

        y += 5;
        context.drawTextWithShadow(textRenderer, "----------------", x, y, 0x444444);
        y += 12;

        // Coordinates
        BlockPos pos = client.player.getBlockPos();
        context.drawTextWithShadow(textRenderer,
                String.format("XYZ: %d / %d / %d", pos.getX(), pos.getY(), pos.getZ()),
                x, y, 0x00CCFF);
        y += 11;

        // Direction
        String facing = getDirection(client.player.getYaw());
        context.drawTextWithShadow(textRenderer, "Yon: " + facing, x, y, 0x00CCFF);
        y += 11;

        // FPS
        context.drawTextWithShadow(textRenderer, "FPS: " + client.getCurrentFps(), x, y, 0xAAAAAA);
        y += 16;

        // Entity counter when ESP is on
        if (moduleManager.isEnabled("esp") && client.world != null) {
            context.drawTextWithShadow(textRenderer, "--- ESP ---", x, y, 0x444444);
            y += 12;

            int hostile = 0, passive = 0, players = 0;
            for (Entity entity : client.world.getEntities()) {
                if (entity instanceof HostileEntity) hostile++;
                else if (entity instanceof AnimalEntity) passive++;
                else if (entity instanceof PlayerEntity && entity != client.player) players++;
            }

            context.drawTextWithShadow(textRenderer, "Dusman: " + hostile, x, y, 0xFF4444);
            y += 11;
            context.drawTextWithShadow(textRenderer, "Pasif: " + passive, x, y, 0x44FF44);
            y += 11;
            context.drawTextWithShadow(textRenderer, "Oyuncu: " + players, x, y, 0xFFFF00);
            y += 16;
        }

        // Health & Hunger
        context.drawTextWithShadow(textRenderer, "----------------", x, y, 0x444444);
        y += 12;

        float health = client.player.getHealth();
        int maxHealth = (int) client.player.getMaxHealth();
        int healthColor = health > 10 ? 0x00FF00 : (health > 5 ? 0xFFFF00 : 0xFF0000);
        context.drawTextWithShadow(textRenderer,
                String.format("Can: %.0f/%d", health, maxHealth), x, y, healthColor);
        y += 11;

        int food = client.player.getHungerManager().getFoodLevel();
        int foodColor = food > 12 ? 0x00FF00 : (food > 6 ? 0xFFFF00 : 0xFF0000);
        context.drawTextWithShadow(textRenderer, "Aclik: " + food + "/20", x, y, foodColor);
        y += 11;

        context.drawTextWithShadow(textRenderer, "Zirh: " + client.player.getArmor(), x, y, 0xCCCCCC);
        y += 15;

        // Keybind hints
        context.drawTextWithShadow(textRenderer, "F2:XRay F3:ESP", x, y, 0x666666);
        y += 11;
        context.drawTextWithShadow(textRenderer, "F4:Bright F6:HUD", x, y, 0x666666);
    }

    private static String getDirection(float yaw) {
        yaw = ((yaw % 360) + 360) % 360;
        if (yaw >= 315 || yaw < 45) return "Guney (S)";
        if (yaw >= 45 && yaw < 135) return "Bati (W)";
        if (yaw >= 135 && yaw < 225) return "Kuzey (N)";
        return "Dogu (E)";
    }
}
