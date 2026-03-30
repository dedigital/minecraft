package com.mchelper.mod.mixin;

import com.mchelper.mod.MCHelperMod;
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

/**
 * X-Ray Mixin - Makes non-ore blocks transparent so you can see ores through walls.
 * When X-Ray is enabled, only valuable blocks are rendered as opaque.
 */
@Mixin(Block.class)
public class XRayMixin {

    // Blocks that should remain visible when X-Ray is active
    private static final Set<Block> XRAY_VISIBLE_BLOCKS = Set.of(
            // Ores
            Blocks.DIAMOND_ORE, Blocks.DEEPSLATE_DIAMOND_ORE,
            Blocks.EMERALD_ORE, Blocks.DEEPSLATE_EMERALD_ORE,
            Blocks.GOLD_ORE, Blocks.DEEPSLATE_GOLD_ORE, Blocks.NETHER_GOLD_ORE,
            Blocks.IRON_ORE, Blocks.DEEPSLATE_IRON_ORE,
            Blocks.COAL_ORE, Blocks.DEEPSLATE_COAL_ORE,
            Blocks.LAPIS_ORE, Blocks.DEEPSLATE_LAPIS_ORE,
            Blocks.REDSTONE_ORE, Blocks.DEEPSLATE_REDSTONE_ORE,
            Blocks.COPPER_ORE, Blocks.DEEPSLATE_COPPER_ORE,
            Blocks.NETHER_QUARTZ_ORE,
            Blocks.ANCIENT_DEBRIS,

            // Valuable blocks
            Blocks.DIAMOND_BLOCK, Blocks.EMERALD_BLOCK, Blocks.GOLD_BLOCK,
            Blocks.IRON_BLOCK, Blocks.NETHERITE_BLOCK,

            // Important blocks
            Blocks.CHEST, Blocks.ENDER_CHEST, Blocks.TRAPPED_CHEST,
            Blocks.SPAWNER,
            Blocks.END_PORTAL_FRAME, Blocks.END_PORTAL,
            Blocks.NETHER_PORTAL,
            Blocks.ENCHANTING_TABLE,
            Blocks.BEACON,
            Blocks.OBSIDIAN,

            // Liquids
            Blocks.LAVA, Blocks.WATER,

            // Bedrock (for reference)
            Blocks.BEDROCK
    );

    /**
     * Inject into shouldDrawSide to control block face rendering.
     * When X-Ray is on, non-valuable blocks become invisible.
     */
    @Inject(method = "shouldDrawSide", at = @At("HEAD"), cancellable = true)
    private static void onShouldDrawSide(BlockState state, BlockView world, BlockPos pos,
                                          Direction side, BlockPos neighborPos,
                                          CallbackInfoReturnable<Boolean> cir) {
        if (MCHelperMod.moduleManager != null && MCHelperMod.moduleManager.isEnabled("xray")) {
            Block block = state.getBlock();
            if (XRAY_VISIBLE_BLOCKS.contains(block)) {
                cir.setReturnValue(true); // Always draw ore faces
            } else {
                cir.setReturnValue(false); // Hide non-ore blocks
            }
        }
    }
}
