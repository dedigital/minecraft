package com.mchelper.mod.mixin;

import com.mchelper.mod.MCHelperMod;
import net.minecraft.client.render.LightmapTextureManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Fullbright Mixin - Makes everything fully lit so you can see in the dark.
 * Overrides the lightmap to always return maximum brightness.
 */
@Mixin(LightmapTextureManager.class)
public class FullbrightMixin {

    @Inject(method = "getBrightness", at = @At("HEAD"), cancellable = true)
    private static void onGetBrightness(float value, CallbackInfoReturnable<Float> cir) {
        if (MCHelperMod.moduleManager != null && MCHelperMod.moduleManager.isEnabled("fullbright")) {
            cir.setReturnValue(1.0f); // Maximum brightness
        }
    }
}
