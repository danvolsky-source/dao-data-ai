/**
 * Unit Tests for advancedApi Service
 * Tests API calls, helper functions, and error handling
 */

import {
  getPrediction,
  getScore,
  getAlerts,
  getSentiment,
  formatPrediction,
  getPredictionColor,
  getScoreColor,
} from '../advancedApi';

// Mock fetch globally
global.fetch = jest.fn();

describe('advancedApi Service', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  describe('getPrediction', () => {
    it('should fetch prediction successfully', async () => {
      const mockData = {
        status: 'success',
        data: {
          proposal_id: 'test-1',
          prediction: 0.85,
          confidence: 0.9,
          model: 'random_forest',
        },
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        json: async () => mockData,
      });

      const result = await getPrediction('test-1');
      expect(result).toEqual(mockData.data);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/advanced/predictions/test-1')
      );
    });

    it('should return null on error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
      const result = await getPrediction('test-1');
      expect(result).toBeNull();
    });
  });

  describe('getScore', () => {
    it('should fetch score successfully', async () => {
      const mockData = {
        status: 'success',
        data: {
          proposal_id: 'test-1',
          overall_score: 85,
          total_score: 85,
          rating: 'EXCELLENT' as const,
        },
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        json: async () => mockData,
      });

      const result = await getScore('test-1');
      expect(result).toEqual(mockData.data);
    });
  });

  describe('getAlerts', () => {
    it('should fetch alerts without severity filter', async () => {
      const mockData = {
        status: 'success',
        data: [{ severity: 'HIGH' as const, message: 'Test alert' }],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        json: async () => mockData,
      });

      const result = await getAlerts();
      expect(result).toEqual(mockData.data);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/advanced/alerts')
      );
    });

    it('should fetch alerts with severity filter', async () => {
      const mockData = { status: 'success', data: [] };
      (fetch as jest.Mock).mockResolvedValueOnce({
        json: async () => mockData,
      });

      await getAlerts('CRITICAL');
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('severity=CRITICAL')
      );
    });
  });

  describe('getSentiment', () => {
    it('should fetch sentiment successfully', async () => {
      const mockData = {
        status: 'success',
        data: {
          proposal_id: 'test-1',
          overall_sentiment: 0.7,
          sentiment_label: 'positive',
          positive_ratio: 0.7,
          negative_ratio: 0.2,
          neutral_ratio: 0.1,
          message_count: 100,
          top_topics: ['governance'],
        },
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        json: async () => mockData,
      });

      const result = await getSentiment('test-1');
      expect(result).toEqual(mockData.data);
    });
  });

  describe('Helper Functions', () => {
    describe('formatPrediction', () => {
      it('should format prediction as percentage', () => {
        expect(formatPrediction(0.75)).toBe('75%');
        expect(formatPrediction(0.333)).toBe('33%');
        expect(formatPrediction(1.0)).toBe('100%');
      });
    });

    describe('getPredictionColor', () => {
      it('should return green for high prediction', () => {
        expect(getPredictionColor(0.8)).toBe('green');
      });

      it('should return yellow for medium prediction', () => {
        expect(getPredictionColor(0.6)).toBe('yellow');
      });

      it('should return red for low prediction', () => {
        expect(getPredictionColor(0.4)).toBe('red');
      });
    });

    describe('getScoreColor', () => {
      it('should return correct colors for ratings', () => {
        expect(getScoreColor('EXCELLENT')).toBe('green');
        expect(getScoreColor('GOOD')).toBe('blue');
        expect(getScoreColor('MODERATE')).toBe('yellow');
        expect(getScoreColor('POOR')).toBe('orange');
        expect(getScoreColor('CRITICAL')).toBe('red');
        expect(getScoreColor('UNKNOWN')).toBe('gray');
      });
    });
  });
});
