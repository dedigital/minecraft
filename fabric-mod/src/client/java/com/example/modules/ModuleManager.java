package com.example.modules;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.LinkedHashMap;
import java.util.Map;

public class ModuleManager {

    private static final Logger LOGGER = LoggerFactory.getLogger("mchelper");
    private final Map<String, Module> modules = new LinkedHashMap<>();

    public ModuleManager() {
        modules.put("xray", new Module("X-Ray", "Cevherleri bloklarin arkasinda goster"));
        modules.put("fullbright", new Module("Fullbright", "Karanlikta gorme"));
    }

    public void toggle(String name) {
        Module module = modules.get(name);
        if (module != null) {
            module.toggle();
            String status = module.isEnabled() ? "ACILDI" : "KAPANDI";
            LOGGER.info("[MC Helper] {} {}", module.getName(), status);
        }
    }

    public boolean isEnabled(String name) {
        Module module = modules.get(name);
        return module != null && module.isEnabled();
    }

    public Map<String, Module> getModules() { return modules; }
}
