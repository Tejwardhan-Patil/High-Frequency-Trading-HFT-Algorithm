package tests;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import org.junit.Test;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import risk_management.compliance;

public class TestRiskManagement {

    @Test
    public void testRiskLimitsFromPython() {
        // This test will invoke the Python script "limits.py" to check if risk limits are enforced correctly
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "risk_management/limits.py", "check_limit");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Python script should return exit code 0", 0, exitCode);
            assertTrue("Risk limit check failed", output.toString().contains("Risk limit passed"));
        } catch (Exception e) {
            fail("Exception in invoking Python script: " + e.getMessage());
        }
    }

    @Test
    public void testExceedingRiskLimits() {
        // This test will check if exceeding the predefined risk limits triggers an error in limits.py
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "risk_management/limits.py", "exceed_limit");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Python script should return exit code 1 for limit exceeded", 1, exitCode);
            assertTrue("Risk limit exceeded test failed", output.toString().contains("Risk limit exceeded"));
        } catch (Exception e) {
            fail("Exception in invoking Python script: " + e.getMessage());
        }
    }

    @Test
    public void testRealTimeMonitoringFromPython() {
        // This test will invoke the Python script "real_time_monitoring.py" to check real-time monitoring
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "risk_management/real_time_monitoring.py", "monitor");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Python script should return exit code 0", 0, exitCode);
            assertTrue("Real-time monitoring failed", output.toString().contains("Monitoring successful"));
        } catch (Exception e) {
            fail("Exception in invoking Python script: " + e.getMessage());
        }
    }

    @Test
    public void testRealTimeMonitoringAlerts() {
        // Test if the real_time_monitoring.py script sends alerts when critical conditions are detected
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "risk_management/real_time_monitoring.py", "trigger_alert");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Python script should return exit code 1 for alert trigger", 1, exitCode);
            assertTrue("Real-time alerting failed", output.toString().contains("Alert triggered"));
        } catch (Exception e) {
            fail("Exception in invoking Python script: " + e.getMessage());
        }
    }

    @Test
    public void testComplianceFromJava() {
        compliance compliance = new compliance(50000);  // Max loss limit set to 50,000
        compliance.setRiskLimit("AAPL", 1000);  // Set risk limit for Apple

        boolean isCompliant = compliance.checkPosition("AAPL", 900);  // Check position
        assertTrue("Position limit check for AAPL failed", isCompliant);
    }

    @Test
    public void testDetailedComplianceCheck() {
        compliance compliance = new compliance(50000);  // Max loss limit set to 50,000
        compliance.setRiskLimit("AAPL", 1000);
        compliance.setRiskLimit("GOOGL", 500);
        compliance.setRiskLimit("TSLA", 800);

        // Check specific compliance for each asset
        boolean resultAAPL = compliance.checkPosition("AAPL", 900);  // Within limit
        boolean resultGOOGL = compliance.checkPosition("GOOGL", 450);  // Within limit
        boolean resultTSLA = compliance.checkPosition("TSLA", 850);  // Exceeds limit

        assertTrue("Position limit check for AAPL failed", resultAAPL);
        assertTrue("Position limit check for GOOGL failed", resultGOOGL);
        assertTrue("Position limit check for TSLA failed", !resultTSLA);  // Expect failure
    }

    @Test
    public void testStressTestingFromCpp() {
        // This test invokes the C++ binary from stress_testing.cpp to run stress tests under different conditions
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("risk_management/stress_test");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Stress test binary should return exit code 0", 0, exitCode);
            assertTrue("Stress test failed", output.toString().contains("Stress test passed"));
        } catch (Exception e) {
            fail("Exception in invoking C++ binary: " + e.getMessage());
        }
    }

    @Test
    public void testMarketCrashStressScenario() {
        // Stress test for extreme market crash scenario, testing system resilience
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("risk_management/stress_test", "market_crash");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Stress test binary should return exit code 0", 0, exitCode);
            assertTrue("Market crash scenario failed", output.toString().contains("Market crash handled"));
        } catch (Exception e) {
            fail("Exception in invoking C++ binary for market crash scenario: " + e.getMessage());
        }
    }

    @Test
    public void testHighVolatilityStressScenario() {
        // Stress test for a high volatility market scenario, testing risk management during extreme fluctuations
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("risk_management/stress_test", "high_volatility");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Stress test binary should return exit code 0", 0, exitCode);
            assertTrue("High volatility scenario failed", output.toString().contains("High volatility handled"));
        } catch (Exception e) {
            fail("Exception in invoking C++ binary for high volatility scenario: " + e.getMessage());
        }
    }

    @Test
    public void testMultipleRiskComponents() {
        // This test combines multiple risk components in a single scenario
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "risk_management/limits.py", "combined_check");
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            int exitCode = process.waitFor();
            assertEquals("Python script should return exit code 0", 0, exitCode);
            assertTrue("Combined risk component check failed", output.toString().contains("Combined risk check passed"));
        } catch (Exception e) {
            fail("Exception in invoking combined risk components: " + e.getMessage());
        }
    }
}