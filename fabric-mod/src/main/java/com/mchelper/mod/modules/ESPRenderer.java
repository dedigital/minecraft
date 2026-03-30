package com.mchelper.mod.modules;

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

/**
 * ESP Renderer - Draws colored bounding boxes around entities.
 *
 * Colors:
 * - Red: Hostile mobs (zombies, skeletons, creepers, etc.)
 * - Green: Passive mobs (cows, sheep, pigs, etc.)
 * - Yellow: Players
 * - Purple: Villagers
 * - Cyan: Dropped items
 */
public class ESPRenderer {

    public static void render(Matrix4f matrix, Camera camera) {
        MinecraftClient client = MinecraftClient.getInstance();
        if (client.world == null || client.player == null) return;

        Vec3d cameraPos = camera.getPos();

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.disableDepthTest();
        RenderSystem.setShader(GameRenderer::getPositionColorProgram);

        Tessellator tessellator = Tessellator.getInstance();

        for (Entity entity : client.world.getEntities()) {
            if (entity == client.player) continue; // Skip self

            // Determine color based on entity type
            float r, g, b;
            if (entity instanceof HostileEntity) {
                r = 1.0f; g = 0.0f; b = 0.0f; // Red
            } else if (entity instanceof PlayerEntity) {
                r = 1.0f; g = 1.0f; b = 0.0f; // Yellow
            } else if (entity instanceof VillagerEntity) {
                r = 0.7f; g = 0.0f; b = 1.0f; // Purple
            } else if (entity instanceof AnimalEntity) {
                r = 0.0f; g = 1.0f; b = 0.0f; // Green
            } else if (entity instanceof ItemEntity) {
                r = 0.0f; g = 1.0f; b = 1.0f; // Cyan
            } else {
                r = 1.0f; g = 1.0f; b = 1.0f; // White for others
            }

            // Get entity bounding box relative to camera
            Box box = entity.getBoundingBox().offset(cameraPos.negate());

            // Draw wireframe box
            drawBox(tessellator, matrix, box, r, g, b, 0.8f);
        }

        RenderSystem.enableDepthTest();
        RenderSystem.disableBlend();
    }

    private static void drawBox(Tessellator tessellator, Matrix4f matrix,
                                 Box box, float r, float g, float b, float a) {
        float x1 = (float) box.minX;
        float y1 = (float) box.minY;
        float z1 = (float) box.minZ;
        float x2 = (float) box.maxX;
        float y2 = (float) box.maxY;
        float z2 = (float) box.maxZ;

        BufferBuilder buffer = tessellator.begin(VertexFormat.DrawMode.DEBUG_LINES, VertexFormats.POSITION_COLOR);

        // Bottom face
        buffer.vertex(matrix, x1, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x2, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y1, z1).color(r, g, b, a);

        // Top face
        buffer.vertex(matrix, x1, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z1).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x2, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z2).color(r, g, b, a);
        buffer.vertex(matrix, x1, y2, z1).color(r, g, b, a);

        // Vertical edges
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
