package com.example.mixin.client;

import com.example.MCHelperClient;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Set;

@Mixin(Block.class)
public class XRayMixin {

    // Blocks to show through X-Ray (ores and valuable blocks)
    private static final Set<Block> XRAY_BLOCKS = Set.of(
            Blocks.DIAMOND_ORE, Blocks.DEEPSLATE_DIAMOND_ORE,
            Blocks.IRON_ORE, Blocks.DEEPSLATE_IRON_ORE,
            Blocks.GOLD_ORE, Blocks.DEEPSLATE_GOLD_ORE,
            Blocks.EMERALD_ORE, Blocks.DEEPSLATE_EMERALD_ORE,
            Blocks.LAPIS_ORE, Blocks.DEEPSLATE_LAPIS_ORE,
            Blocks.REDSTONE_ORE, Blocks.DEEPSLATE_REDSTONE_ORE,
            Blocks.COPPER_ORE, Blocks.DEEPSLATE_COPPER_ORE,
            Blocks.COAL_ORE, Blocks.DEEPSLATE_COAL_ORE,
            Blocks.ANCIENT_DEBRIS,
            Blocks.NETHER_GOLD_ORE, Blocks.NETHER_QUARTZ_ORE,
            Blocks.CHEST, Blocks.ENDER_CHEST, Blocks.TRAPPED_CHEST,
            Blocks.SPAWNER,
            Blocks.DIAMOND_BLOCK, Blocks.EMERALD_BLOCK, Blocks.GOLD_BLOCK,
            Blocks.TNT, Blocks.OBSIDIAN, Blocks.CRYING_OBSIDIAN
    );

    @Inject(method = "shouldRenderFace", at = @At("RETURN"), cancellable = true)
    private static void onShouldRenderFace(BlockState state, BlockState adjacentState,
                                            Direction side, CallbackInfoReturnable<Boolean> cir) {
        if (MCHelperClient.moduleManager != null && MCHelperClient.moduleManager.isEnabled("xray")) {
            Block block = state.getBlock();
            if (XRAY_BLOCKS.contains(block)) {
                // Always render faces of valuable blocks
                cir.setReturnValue(true);
            } else {
                // Hide all other blocks
                cir.setReturnValue(false);
            }
        }
    }
}
