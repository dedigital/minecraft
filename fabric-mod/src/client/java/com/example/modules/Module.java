package com.example.modules;

public class Module {
    private final String name;
    private final String description;
    private final String key;
    private final String category;
    private boolean enabled;

    public Module(String name, String description, String key, String category) {
        this.name = name;
        this.description = description;
        this.key = key;
        this.category = category;
        this.enabled = false;
    }

    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getKey() { return key; }
    public String getCategory() { return category; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public void toggle() { this.enabled = !this.enabled; }
}
