package com.example.modules;

import net.minecraft.client.MinecraftClient;
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;

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
            MinecraftClient client = MinecraftClient.getInstance();
            if (client != null && client.player != null) {
                String status = module.isEnabled() ? "ACILDI" : "KAPANDI";
                Formatting color = module.isEnabled() ? Formatting.GREEN : Formatting.RED;
                client.player.sendMessage(
                        Text.literal("[MC Helper] " + module.getName() + " " + status).formatted(color),
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
