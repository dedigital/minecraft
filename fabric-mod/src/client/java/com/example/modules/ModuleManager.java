package com.example.modules;

import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.ChatFormatting;

import java.util.LinkedHashMap;
import java.util.Map;

public class ModuleManager {

    private final Map<String, Module> modules = new LinkedHashMap<>();

    public ModuleManager() {
        modules.put("xray", new Module("X-Ray", "Cevherleri bloklarin arkasinda goster"));
        modules.put("esp", new Module("ESP", "Moblari ve oyunculari isaretler"));
        modules.put("fullbright", new Module("Fullbright", "Karanlikta gorme"));
        modules.put("hud", new Module("HUD", "Bilgi ekrani"));
        modules.get("hud").setEnabled(true);
    }

    public void toggle(String name) {
        Module module = modules.get(name);
        if (module != null) {
            module.toggle();
            Minecraft client = Minecraft.getInstance();
            if (client != null && client.player != null) {
                String status = module.isEnabled() ? "ACILDI" : "KAPANDI";
                ChatFormatting color = module.isEnabled() ? ChatFormatting.GREEN : ChatFormatting.RED;
                client.player.displayClientMessage(
                        Component.literal("[MC Helper] " + module.getName() + " " + status).withStyle(color),
                        true
                );
            }
        }
    }

    public boolean isEnabled(String name) {
        Module module = modules.get(name);
        return module != null && module.isEnabled();
    }

    public Map<String, Module> getModules() { return modules; }
}
