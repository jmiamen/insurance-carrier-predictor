import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// Common medications list for autocomplete
const COMMON_MEDICATIONS = [
  'Metformin', 'Ozempic', 'Insulin', 'Lantus', 'Humalog', 'Novolog', 'Jardiance',
  'Lisinopril', 'Amlodipine', 'Losartan',
  'Atorvastatin', 'Lipitor', 'Rosuvastatin', 'Crestor', 'Simvastatin', 'Zocor',
  'Levothyroxine', 'Synthroid',
  'Aspirin', 'Metoprolol', 'Lopressor',
  'Clopidogrel', 'Plavix', 'Warfarin', 'Coumadin', 'Eliquis', 'Apixaban',
  'Albuterol', 'Ventolin', 'Advair', 'Spiriva',
  'Sertraline', 'Zoloft', 'Escitalopram', 'Lexapro', 'Wellbutrin',
  'Xanax', 'Alprazolam',
  'Lithium', 'Seroquel', 'Quetiapine'
];

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

function App() {
  const [formData, setFormData] = useState({
    age: '',
    state: 'TX',
    gender: 'M',
    smoker: false,
    coverage_type: 'Term',
    desired_coverage: '',
    health_conditions: '',
    medications: []
  });

  const [medicationInput, setMedicationInput] = useState('');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const addMedication = (medication) => {
    if (medication && !formData.medications.includes(medication)) {
      setFormData(prev => ({
        ...prev,
        medications: [...prev.medications, medication]
      }));
      setMedicationInput('');
    }
  };

  const removeMedication = (medication) => {
    setFormData(prev => ({
      ...prev,
      medications: prev.medications.filter(m => m !== medication)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRecommendations(null);

    try {
      const payload = {
        age: parseInt(formData.age),
        state: formData.state,
        gender: formData.gender,
        smoker: formData.smoker,
        coverage_type: formData.coverage_type,
        desired_coverage: parseInt(formData.desired_coverage),
        health_conditions: formData.health_conditions ? formData.health_conditions.split(',').map(c => c.trim()) : [],
        medications: formData.medications
      };

      const response = await axios.post('/recommend-carriers', payload);
      setRecommendations(response.data.recommendations);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error getting recommendations. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🏥 Insurance Carrier Predictor</h1>
          <p>Find the best carrier match based on client health and medications</p>
        </header>

        <div className="content">
          <form onSubmit={handleSubmit} className="form-card">
            <h2>Client Information</h2>

            <div className="form-row">
              <div className="form-group">
                <label>Age</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  required
                  min="0"
                  max="100"
                  placeholder="55"
                />
              </div>

              <div className="form-group">
                <label>State</label>
                <select name="state" value={formData.state} onChange={handleInputChange}>
                  {US_STATES.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Gender</label>
                <select name="gender" value={formData.gender} onChange={handleInputChange}>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Coverage Type</label>
                <select name="coverage_type" value={formData.coverage_type} onChange={handleInputChange}>
                  <option value="Term">Term</option>
                  <option value="Whole Life">Whole Life</option>
                  <option value="IUL">IUL</option>
                  <option value="Final Expense">Final Expense</option>
                  <option value="Universal Life">Universal Life</option>
                </select>
              </div>

              <div className="form-group">
                <label>Desired Coverage ($)</label>
                <input
                  type="number"
                  name="desired_coverage"
                  value={formData.desired_coverage}
                  onChange={handleInputChange}
                  required
                  min="1000"
                  step="1000"
                  placeholder="250000"
                />
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="smoker"
                    checked={formData.smoker}
                    onChange={handleInputChange}
                  />
                  Smoker
                </label>
              </div>
            </div>

            <div className="form-group">
              <label>Current Medications</label>
              <div className="medication-input-container">
                <input
                  type="text"
                  value={medicationInput}
                  onChange={(e) => setMedicationInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addMedication(medicationInput);
                    }
                  }}
                  placeholder="Type medication name..."
                  list="medications-list"
                />
                <button
                  type="button"
                  onClick={() => addMedication(medicationInput)}
                  className="add-btn"
                >
                  Add
                </button>
              </div>
              <datalist id="medications-list">
                {COMMON_MEDICATIONS.map(med => (
                  <option key={med} value={med} />
                ))}
              </datalist>

              {formData.medications.length > 0 && (
                <div className="medication-tags">
                  {formData.medications.map(med => (
                    <span key={med} className="medication-tag">
                      {med}
                      <button
                        type="button"
                        onClick={() => removeMedication(med)}
                        className="remove-tag"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Health Conditions (comma-separated)</label>
              <input
                type="text"
                name="health_conditions"
                value={formData.health_conditions}
                onChange={handleInputChange}
                placeholder="diabetes controlled, high blood pressure"
              />
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Finding Carriers...' : 'Get Recommendations'}
            </button>
          </form>

          {error && (
            <div className="error-card">
              <h3>⚠️ Error</h3>
              <p>{error}</p>
            </div>
          )}

          {recommendations && recommendations.length > 0 && (
            <div className="results-card">
              <h2>📊 Recommended Carriers</h2>
              <div className="recommendations-grid">
                {recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-card">
                    <div className="rec-header">
                      <h3>{rec.carrier}</h3>
                      <span className="confidence-badge">
                        {Math.round(rec.confidence * 100)}% Match
                      </span>
                    </div>
                    <div className="rec-body">
                      <p className="product-name">{rec.product}</p>
                      <p className="reason">{rec.reason}</p>
                      {rec.portal_url && (
                        <a
                          href={rec.portal_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="portal-link"
                        >
                          Go to Portal →
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {recommendations && recommendations.length === 0 && (
            <div className="no-results-card">
              <h3>No Recommendations Found</h3>
              <p>Try adjusting the criteria or contact underwriting for special cases.</p>
            </div>
          )}
        </div>

        <footer className="footer">
          <p>💡 Powered by AI-driven carrier matching</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
