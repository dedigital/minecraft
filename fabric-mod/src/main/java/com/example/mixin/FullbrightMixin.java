package com.example.mixin;

import com.example.MCHelperMod;
import net.minecraft.client.render.LightmapTextureManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(LightmapTextureManager.class)
public class FullbrightMixin {

    @Inject(method = "getBrightness", at = @At("HEAD"), cancellable = true)
    private static void onGetBrightness(float value, CallbackInfoReturnable<Float> cir) {
        if (MCHelperMod.moduleManager != null && MCHelperMod.moduleManager.isEnabled("fullbright")) {
            cir.setReturnValue(1.0f);
        }
    }
}
