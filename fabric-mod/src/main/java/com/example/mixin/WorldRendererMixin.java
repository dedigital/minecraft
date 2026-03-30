package com.example.mixin;

import com.example.MCHelperMod;
import com.example.modules.ESPRenderer;
import net.minecraft.client.render.WorldRenderer;
import net.minecraft.client.render.Camera;
import net.minecraft.client.render.GameRenderer;
import net.minecraft.client.render.LightmapTextureManager;
import net.minecraft.client.render.RenderTickCounter;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

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
