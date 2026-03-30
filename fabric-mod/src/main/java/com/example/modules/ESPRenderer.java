package com.example.modules;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.render.*;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.passive.AnimalEntity;
import net.minecraft.entity.passive.VillagerEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.ItemEntity;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import org.joml.Matrix4f;

public class ESPRenderer {

    public static void render(Matrix4f matrix, Camera camera) {
        MinecraftClient client = MinecraftClient.getInstance();
        if (client.world == null || client.player == null) return;

        Vec3d cameraPos = camera.getPos();

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.disableDepthTest();

        Tessellator tessellator = Tessellator.getInstance();

        for (Entity entity : client.world.getEntities()) {
            if (entity == client.player) continue;

            float r, g, b;
            if (entity instanceof HostileEntity) {
                r = 1.0f; g = 0.0f; b = 0.0f;
            } else if (entity instanceof PlayerEntity) {
                r = 1.0f; g = 1.0f; b = 0.0f;
            } else if (entity instanceof VillagerEntity) {
                r = 0.7f; g = 0.0f; b = 1.0f;
            } else if (entity instanceof AnimalEntity) {
                r = 0.0f; g = 1.0f; b = 0.0f;
            } else if (entity instanceof ItemEntity) {
                r = 0.0f; g = 1.0f; b = 1.0f;
            } else {
                r = 1.0f; g = 1.0f; b = 1.0f;
            }

            Box box = entity.getBoundingBox().offset(cameraPos.negate());
            drawBox(tessellator, matrix, box, r, g, b, 0.8f);
        }

        RenderSystem.enableDepthTest();
        RenderSystem.disableBlend();
    }

    private static void drawBox(Tessellator tessellator, Matrix4f matrix,
                                 Box box, float r, float g, float b, float a) {
        float x1 = (float) box.minX, y1 = (float) box.minY, z1 = (float) box.minZ;
        float x2 = (float) box.maxX, y2 = (float) box.maxY, z2 = (float) box.maxZ;

        BufferBuilder buffer = tessellator.begin(VertexFormat.DrawMode.DEBUG_LINES, VertexFormats.POSITION_COLOR);

        // Bottom
        buffer.vertex(matrix, x1, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z1).color(r, g, b, a);

        // Top
        buffer.vertex(matrix, x1, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z1).color(r, g, b, a);

        // Verticals
        buffer.vertex(matrix, x1, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z2).color(r, g, b, a);

        BufferRenderer.drawWithGlobalProgram(buffer.end());
    }
}
