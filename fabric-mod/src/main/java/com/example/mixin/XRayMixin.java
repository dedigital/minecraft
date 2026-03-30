package com.example.mixin;

import com.example.MCHelperMod;
import net.minecraft.block.Block;
import net.minecraft.block.BlockState;
import net.minecraft.block.Blocks;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Direction;
import net.minecraft.world.BlockView;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Set;

@Mixin(Block.class)
public class XRayMixin {

    private static final Set<Block> XRAY_VISIBLE = Set.of(
            Blocks.DIAMOND_ORE, Blocks.DEEPSLATE_DIAMOND_ORE,
            Blocks.EMERALD_ORE, Blocks.DEEPSLATE_EMERALD_ORE,
            Blocks.GOLD_ORE, Blocks.DEEPSLATE_GOLD_ORE, Blocks.NETHER_GOLD_ORE,
            Blocks.IRON_ORE, Blocks.DEEPSLATE_IRON_ORE,
            Blocks.COAL_ORE, Blocks.DEEPSLATE_COAL_ORE,
            Blocks.LAPIS_ORE, Blocks.DEEPSLATE_LAPIS_ORE,
            Blocks.REDSTONE_ORE, Blocks.DEEPSLATE_REDSTONE_ORE,
            Blocks.COPPER_ORE, Blocks.DEEPSLATE_COPPER_ORE,
            Blocks.NETHER_QUARTZ_ORE, Blocks.ANCIENT_DEBRIS,
            Blocks.DIAMOND_BLOCK, Blocks.EMERALD_BLOCK,
            Blocks.GOLD_BLOCK, Blocks.IRON_BLOCK, Blocks.NETHERITE_BLOCK,
            Blocks.CHEST, Blocks.ENDER_CHEST, Blocks.TRAPPED_CHEST,
            Blocks.SPAWNER, Blocks.ENCHANTING_TABLE, Blocks.BEACON,
            Blocks.END_PORTAL_FRAME, Blocks.END_PORTAL, Blocks.NETHER_PORTAL,
            Blocks.OBSIDIAN, Blocks.BEDROCK,
            Blocks.LAVA, Blocks.WATER
    );

    @Inject(method = "shouldDrawSide", at = @At("HEAD"), cancellable = true)
    private static void onShouldDrawSide(BlockState state, BlockView world, BlockPos pos,
                                          Direction side, BlockPos neighborPos,
                                          CallbackInfoReturnable<Boolean> cir) {
        if (MCHelperMod.moduleManager != null && MCHelperMod.moduleManager.isEnabled("xray")) {
            cir.setReturnValue(XRAY_VISIBLE.contains(state.getBlock()));
        }
    }
}
