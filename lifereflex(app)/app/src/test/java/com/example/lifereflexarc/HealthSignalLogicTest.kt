package com.example.lifereflexarc

import com.example.lifereflexarc.data.HealthCondition
import com.example.lifereflexarc.data.HealthSignalLogic
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthSignalLogicTest {

    @Test
    fun riskTags_tachycardia_whenHrAboveThreshold() {
        assertEquals(listOf("tachycardia"), HealthSignalLogic.buildRiskTags(118, 98.0))
    }

    @Test
    fun riskTags_bradycardia_whenHrBelowThreshold() {
        assertEquals(listOf("bradycardia"), HealthSignalLogic.buildRiskTags(52, 98.0))
    }

    @Test
    fun riskTags_lowSpo2_whenBelow95() {
        assertEquals(listOf("low_spo2"), HealthSignalLogic.buildRiskTags(80, 92.0))
    }

    @Test
    fun riskTags_combinedWhenMultipleRisks() {
        assertEquals(
            listOf("tachycardia", "low_spo2"),
            HealthSignalLogic.buildRiskTags(118, 90.0),
        )
    }

    @Test
    fun riskTags_empty_whenNoRisk() {
        assertTrue(HealthSignalLogic.buildRiskTags(80, 98.0).isEmpty())
    }

    @Test
    fun riskTags_empty_whenValuesNull() {
        assertTrue(HealthSignalLogic.buildRiskTags(null, null).isEmpty())
    }

    @Test
    fun riskTags_boundary_bpm100IsTachycardia() {
        assertTrue(HealthSignalLogic.buildRiskTags(100, 98.0).contains("tachycardia"))
    }

    @Test
    fun riskTags_boundary_bpm60IsBradycardia() {
        assertTrue(HealthSignalLogic.buildRiskTags(60, 98.0).contains("bradycardia"))
    }

    @Test
    fun riskTags_boundary_spo2_95IsNotLow() {
        assertTrue(HealthSignalLogic.buildRiskTags(80, 95.0).isEmpty())
    }

    @Test
    fun sleepQuality_good_whenLongEnough() {
        assertEquals("good", HealthSignalLogic.sleepQuality(8.0))
    }

    @Test
    fun sleepQuality_fair_whenModerate() {
        assertEquals("fair", HealthSignalLogic.sleepQuality(6.0))
    }

    @Test
    fun sleepQuality_poor_whenShort() {
        assertEquals("poor", HealthSignalLogic.sleepQuality(3.0))
    }

    @Test
    fun sleepQuality_boundary_7hIsGood() {
        assertEquals("good", HealthSignalLogic.sleepQuality(7.0))
    }

    @Test
    fun activityLevel_high_whenOver10000Steps() {
        assertEquals("high", HealthSignalLogic.activityLevel(12_000))
    }

    @Test
    fun activityLevel_normal_whenModerate() {
        assertEquals("normal", HealthSignalLogic.activityLevel(7_500))
    }

    @Test
    fun activityLevel_low_whenFewSteps() {
        assertEquals("low", HealthSignalLogic.activityLevel(2_000))
    }

    @Test
    fun activityLevel_null_whenNoData() {
        assertNull(HealthSignalLogic.activityLevel(null))
    }

    @Test
    fun pressureScore_mapsConditions() {
        assertEquals(78, HealthSignalLogic.pressureScore(HealthCondition.CARDIAC_RISK))
        assertEquals(24, HealthSignalLogic.pressureScore(HealthCondition.ATHLETIC))
        assertEquals(55, HealthSignalLogic.pressureScore(HealthCondition.LIMITED_MOBILITY))
        assertEquals(30, HealthSignalLogic.pressureScore(HealthCondition.GENERAL))
    }

    @Test
    fun fallbackSummary_cardiacRiskFlagsRealisticRisk() {
        val summary = HealthSignalLogic.fallbackSummary(HealthCondition.CARDIAC_RISK)
        assertEquals(118, summary.heartRateBpm)
        assertEquals(92.0, summary.bloodOxygenPercent ?: 0.0, 0.001)
        assertTrue(summary.riskTags.contains("tachycardia"))
        assertTrue(summary.riskTags.contains("low_spo2"))
    }

    @Test
    fun fallbackSummary_athleticIsLowRisk() {
        val summary = HealthSignalLogic.fallbackSummary(HealthCondition.ATHLETIC)
        assertEquals(84, summary.heartRateBpm)
        assertTrue(summary.riskTags.isEmpty())
    }

    @Test
    fun fallbackNote_pendingEncouragesAuthorization() {
        assertTrue(HealthSignalLogic.fallbackNote("pending").contains("授权"))
    }

    @Test
    fun fallbackNote_notConnectedExplainsMissingSdk() {
        assertTrue(HealthSignalLogic.fallbackNote("not_connected").contains("样例摘要"))
    }
}
