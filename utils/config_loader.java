package utils;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

public class config_loader {

    private Properties properties;
    private static config_loader instance;
    private static final Logger logger = Logger.getLogger(config_loader.class.getName());

    // Private constructor for singleton pattern
    private config_loader(String configFilePath) throws IOException {
        properties = new Properties();
        loadConfigFile(configFilePath);
    }

    // Singleton instance accessor
    public static config_loader getInstance(String configFilePath) throws IOException {
        if (instance == null) {
            synchronized (config_loader.class) {
                if (instance == null) {
                    instance = new config_loader(configFilePath);
                }
            }
        }
        return instance;
    }

    // Load configuration from a given file
    private void loadConfigFile(String configFilePath) throws IOException {
        try (FileInputStream inputStream = new FileInputStream(configFilePath)) {
            properties.load(inputStream);
            logger.log(Level.INFO, "Configuration loaded from: {0}", configFilePath);
        } catch (FileNotFoundException e) {
            logger.log(Level.SEVERE, "Configuration file not found: {0}", configFilePath);
            throw new IOException("Configuration file not found", e);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error loading configuration file: {0}", configFilePath);
            throw new IOException("Error loading configuration file", e);
        }
    }

    // Retrieve a configuration value by key
    public String getConfig(String key) {
        validateKey(key);
        String value = properties.getProperty(key);
        if (value != null) {
            logger.log(Level.INFO, "Retrieved config: {0}={1}", new Object[]{key, value});
        } else {
            logger.log(Level.WARNING, "Config key not found: {0}", key);
        }
        return value;
    }

    // Retrieve a configuration value with a default
    public String getConfig(String key, String defaultValue) {
        validateKey(key);
        String value = properties.getProperty(key, defaultValue);
        logger.log(Level.INFO, "Retrieved config with default: {0}={1}", new Object[]{key, value});
        return value;
    }

    // Validate that the key is not null or empty
    private void validateKey(String key) {
        if (key == null || key.trim().isEmpty()) {
            logger.log(Level.SEVERE, "Configuration key cannot be null or empty");
            throw new IllegalArgumentException("Configuration key cannot be null or empty");
        }
    }

    // Check if a key exists in the configuration
    public boolean containsKey(String key) {
        validateKey(key);
        boolean contains = properties.containsKey(key);
        logger.log(Level.INFO, "Config contains key: {0}={1}", new Object[]{key, contains});
        return contains;
    }

    // Reload configuration from the file
    public void reload(String configFilePath) throws IOException {
        try (FileInputStream inputStream = new FileInputStream(configFilePath)) {
            properties.clear();
            properties.load(inputStream);
            logger.log(Level.INFO, "Configuration reloaded from: {0}", configFilePath);
        } catch (FileNotFoundException e) {
            logger.log(Level.SEVERE, "Reload failed, file not found: {0}", configFilePath);
            throw new IOException("Configuration file not found", e);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error reloading configuration: {0}", configFilePath);
            throw new IOException("Error reloading configuration", e);
        }
    }

    // Retrieve all keys from the configuration
    public Set<String> getAllKeys() {
        Set<String> keys = properties.stringPropertyNames();
        logger.log(Level.INFO, "Retrieved all configuration keys");
        return keys;
    }

    // Print all configuration keys and values
    public void printAllConfigs() {
        properties.forEach((key, value) -> {
            logger.log(Level.INFO, "Config: {0}={1}", new Object[]{key, value});
        });
    }

    // Remove a configuration key
    public void removeConfig(String key) {
        validateKey(key);
        if (properties.containsKey(key)) {
            properties.remove(key);
            logger.log(Level.INFO, "Removed config key: {0}", key);
        } else {
            logger.log(Level.WARNING, "Config key not found for removal: {0}", key);
        }
    }

    // Clear all configurations
    public void clearConfigs() {
        properties.clear();
        logger.log(Level.INFO, "All configurations cleared");
    }

    // Save configurations to a file
    public void saveConfig(String configFilePath) throws IOException {
        logger.log(Level.INFO, "Saving configurations to file: {0}", configFilePath);

        try (FileOutputStream outputStream = new FileOutputStream(configFilePath)) {
            // Save properties to the specified file
            properties.store(outputStream, "Configurations saved to file");
            logger.log(Level.INFO, "Configurations successfully saved to file: {0}", configFilePath);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error saving configurations to file: {0}", configFilePath);
            throw e; // Re-throw the exception after logging
        }
    }

    // Log the total number of configurations
    public int getConfigCount() {
        int count = properties.size();
        logger.log(Level.INFO, "Total configurations: {0}", count);
        return count;
    }

    // Load default configuration
    public void loadDefaultConfig() {
        logger.log(Level.INFO, "Loading default configuration");

        try (InputStream inputStream = getClass().getClassLoader().getResourceAsStream("default_config.properties")) {
            if (inputStream != null) {
                properties.load(inputStream);
                logger.log(Level.INFO, "Default configurations loaded from file successfully");
            } else {
                logger.log(Level.SEVERE, "Default configuration file not found");
            }
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error loading default configurations", e);
        }
    }

    // Load environment-specific configurations
    public void loadEnvConfig(String environment) throws IOException {
        logger.log(Level.INFO, "Loading environment-specific configuration: {0}", environment);
        String envConfigFile = getEnvironmentConfigFilePath(environment);
        reload(envConfigFile);
    }

    // Get environment-specific configuration file path
    private String getEnvironmentConfigFilePath(String environment) {
        return "configs/" + environment + "_config.properties";
    }

    // Check if the configuration is empty
    public boolean isConfigEmpty() {
        boolean isEmpty = properties.isEmpty();
        logger.log(Level.INFO, "Configuration empty: {0}", isEmpty);
        return isEmpty;
    }

    // Log the time taken to load configurations
    public void logLoadTime(long startTime, long endTime) {
        long duration = endTime - startTime;
        logger.log(Level.INFO, "Configuration loaded in {0} ms", duration);
    }

    // Log when configuration is being initialized
    public void logInitialization() {
        logger.log(Level.INFO, "Initializing configuration loader");
    }

    // Placeholder method for testing logging
    public void logTest() {
        logger.log(Level.FINE, "Test log message at FINE level");
    }
}