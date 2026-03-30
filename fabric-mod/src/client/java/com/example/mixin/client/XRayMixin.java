package com.example.mixin.client;

import com.example.MCHelperClient;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Set;

@Mixin(Block.class)
public class XRayMixin {

    private static final Set<Block> XRAY_VISIBLE = Set.of(
            // Ores
            Blocks.DIAMOND_ORE, Blocks.DEEPSLATE_DIAMOND_ORE,
            Blocks.EMERALD_ORE, Blocks.DEEPSLATE_EMERALD_ORE,
            Blocks.GOLD_ORE, Blocks.DEEPSLATE_GOLD_ORE, Blocks.NETHER_GOLD_ORE,
            Blocks.IRON_ORE, Blocks.DEEPSLATE_IRON_ORE,
            Blocks.COAL_ORE, Blocks.DEEPSLATE_COAL_ORE,
            Blocks.LAPIS_ORE, Blocks.DEEPSLATE_LAPIS_ORE,
            Blocks.REDSTONE_ORE, Blocks.DEEPSLATE_REDSTONE_ORE,
            Blocks.COPPER_ORE, Blocks.DEEPSLATE_COPPER_ORE,
            Blocks.NETHER_QUARTZ_ORE, Blocks.ANCIENT_DEBRIS,
            // Valuable blocks
            Blocks.DIAMOND_BLOCK, Blocks.EMERALD_BLOCK,
            Blocks.GOLD_BLOCK, Blocks.IRON_BLOCK, Blocks.NETHERITE_BLOCK,
            // Important blocks
            Blocks.CHEST, Blocks.ENDER_CHEST, Blocks.TRAPPED_CHEST,
            Blocks.SPAWNER, Blocks.ENCHANTING_TABLE, Blocks.BEACON,
            Blocks.OBSIDIAN, Blocks.BEDROCK,
            // Liquids
            Blocks.LAVA, Blocks.WATER
    );

    @Inject(method = "shouldRenderFace", at = @At("HEAD"), cancellable = true)
    private static void onShouldRenderFace(BlockState state, BlockGetter level, BlockPos pos,
                                            Direction direction, BlockPos neighborPos,
                                            CallbackInfoReturnable<Boolean> cir) {
        if (MCHelperClient.moduleManager != null && MCHelperClient.moduleManager.isEnabled("xray")) {
            cir.setReturnValue(XRAY_VISIBLE.contains(state.getBlock()));
        }
    }
}
