package com.example.modules;

public class Module {
    private final String name;
    private final String description;
    private final String key;
    private boolean enabled;

    public Module(String name, String description, String key) {
        this.name = name;
        this.description = description;
        this.key = key;
        this.enabled = false;
    }

    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getKey() { return key; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public void toggle() { this.enabled = !this.enabled; }
}
