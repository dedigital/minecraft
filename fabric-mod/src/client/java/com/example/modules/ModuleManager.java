package com.example.modules;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.LinkedHashMap;
import java.util.Map;

public class ModuleManager {

    private static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    private final Map<String, Module> modules = new LinkedHashMap<>();

    // Configurable values
    private double speedMult = 1.8;
    private int zoomFov = 20;
    private double auraRange = 4.0;

    public ModuleManager() {
        // Combat
        modules.put("killaura", new Module("Kill Aura", "Attack nearest hostile mob", "R", "combat"));
        modules.put("antiknockback", new Module("Anti-Knockback", "Reduce knockback by 90%", "B", "combat"));

        // Movement
        modules.put("fly", new Module("Fly", "Creative flight", "H", "movement"));
        modules.put("speed", new Module("Speed", "Faster ground movement", "J", "movement"));
        modules.put("autosprint", new Module("Auto-Sprint", "Automatic sprinting", "K", "movement"));
        modules.put("nofall", new Module("No Fall", "No fall damage", "N", "movement"));
        modules.put("step", new Module("Step Assist", "Step up 1.5 blocks", "V", "movement"));

        // Visual
        modules.put("fullbright", new Module("Fullbright", "See in the dark", "G", "visual"));

        // Player
        modules.put("nohunger", new Module("No Hunger", "Keep hunger full (SP only)", "P", "player"));
    }

    public void toggle(String name) {
        Module module = modules.get(name);
        if (module != null) {
            module.toggle();
            String status = module.isEnabled() ? "ON" : "OFF";
            LOGGER.info("[MC Helper] {} {}", module.getName(), status);
        }
    }

    public boolean isEnabled(String name) {
        Module module = modules.get(name);
        return module != null && module.isEnabled();
    }

    public Map<String, Module> getModules() { return modules; }

    // Config getters/setters
    public double getSpeedMult() { return speedMult; }
    public void setSpeedMult(double speedMult) { this.speedMult = speedMult; }

    public int getZoomFov() { return zoomFov; }
    public void setZoomFov(int zoomFov) { this.zoomFov = zoomFov; }

    public double getAuraRange() { return auraRange; }
    public void setAuraRange(double auraRange) { this.auraRange = auraRange; }
}
