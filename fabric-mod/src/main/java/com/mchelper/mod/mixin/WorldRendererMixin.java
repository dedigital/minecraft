package com.mchelper.mod.mixin;

import com.mchelper.mod.MCHelperMod;
import com.mchelper.mod.modules.ESPRenderer;
import net.minecraft.client.render.WorldRenderer;
import net.minecraft.client.render.Camera;
import net.minecraft.client.render.GameRenderer;
import net.minecraft.client.render.LightmapTextureManager;
import net.minecraft.client.render.RenderTickCounter;
import net.minecraft.client.util.math.MatrixStack;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * World Renderer Mixin - Hooks into world rendering to draw ESP overlays.
 * Renders entity boxes and tracers when ESP is enabled.
 */
@Mixin(WorldRenderer.class)
public class WorldRendererMixin {

    @Inject(method = "render", at = @At("RETURN"))
    private void onRender(RenderTickCounter tickCounter,
                          boolean renderBlockOutline, Camera camera,
                          GameRenderer gameRenderer,
                          LightmapTextureManager lightmapTextureManager,
                          Matrix4f matrix4f, Matrix4f matrix4f2,
                          CallbackInfo ci) {
        if (MCHelperMod.moduleManager != null && MCHelperMod.moduleManager.isEnabled("esp")) {
            ESPRenderer.render(matrix4f, camera);
        }
    }
}
