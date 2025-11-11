import React, { useState, useEffect } from 'react';
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

// Medical condition categories
const MEDICAL_CONDITIONS = {
  cardiovascular: {
    title: 'Cardiovascular',
    icon: '❤️',
    conditions: [
      { id: 'heart_attack', label: 'Heart Attack (MI)', meds: ['Aspirin', 'Atorvastatin', 'Metoprolol'] },
      { id: 'stroke', label: 'Stroke', meds: ['Clopidogrel', 'Atorvastatin', 'Warfarin', 'Apixaban'] },
      { id: 'high_bp', label: 'High Blood Pressure', meds: ['Lisinopril', 'Amlodipine', 'Losartan'] }
    ]
  },
  metabolic: {
    title: 'Metabolic / Endocrine',
    icon: '🩺',
    conditions: [
      { id: 'diabetes', label: 'Diabetes', meds: ['Metformin', 'Ozempic', 'Insulin', 'Jardiance'] },
      { id: 'cholesterol', label: 'High Cholesterol', meds: ['Atorvastatin', 'Rosuvastatin', 'Simvastatin'] },
      { id: 'thyroid', label: 'Thyroid Condition', meds: ['Levothyroxine', 'Synthroid'] }
    ]
  },
  respiratory: {
    title: 'Respiratory',
    icon: '🫁',
    conditions: [
      { id: 'asthma_copd', label: 'Asthma / COPD', meds: ['Albuterol', 'Advair', 'Spiriva'] }
    ]
  },
  mental_health: {
    title: 'Mental Health',
    icon: '🧠',
    conditions: [
      { id: 'anxiety', label: 'Anxiety', meds: ['Sertraline', 'Alprazolam', 'Escitalopram'] },
      { id: 'depression', label: 'Depression', meds: ['Sertraline', 'Escitalopram', 'Wellbutrin'] },
      { id: 'bipolar', label: 'Bipolar Disorder', meds: ['Lithium', 'Quetiapine'] }
    ]
  }
};

function App() {
  const [activeTab, setActiveTab] = useState('quote'); // 'quote' or 'saved'

  const [formData, setFormData] = useState({
    // Contact Info
    first_name: '',
    last_name: '',
    email: '',
    phone: '',

    // Demographics
    age: '',
    dob: '',
    state: 'TX',
    gender: 'M',
    height_ft: '',
    height_in: '',
    weight: '',
    smoker: false,

    // Coverage
    coverage_type: 'Term',
    desired_coverage: '',

    // Financial
    monthly_income: '',
    monthly_expenses: '',

    // Medical conditions
    medical_conditions: {},

    // Additional notes
    notes: ''
  });

  const [expandedCategories, setExpandedCategories] = useState({
    cardiovascular: true,
    metabolic: false,
    respiratory: false,
    mental_health: false
  });

  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savedCases, setSavedCases] = useState([]);

  // Load saved cases on mount
  useEffect(() => {
    loadSavedCases();
  }, []);

  // Auto-calculate age from DOB
  useEffect(() => {
    if (formData.dob) {
      const dob = new Date(formData.dob);
      const today = new Date();
      let age = today.getFullYear() - dob.getFullYear();
      const monthDiff = today.getMonth() - dob.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
        age--;
      }
      if (age > 0 && age < 120) {
        setFormData(prev => ({ ...prev, age: age.toString() }));
      }
    }
  }, [formData.dob]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleMedicalConditionChange = (conditionId, field, value) => {
    setFormData(prev => ({
      ...prev,
      medical_conditions: {
        ...prev.medical_conditions,
        [conditionId]: {
          ...prev.medical_conditions[conditionId],
          [field]: value
        }
      }
    }));
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const calculateLeftover = () => {
    const income = parseFloat(formData.monthly_income) || 0;
    const expenses = parseFloat(formData.monthly_expenses) || 0;
    return income - expenses;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRecommendations(null);

    try {
      // Build medications array from medical conditions
      const medications = [];
      Object.entries(formData.medical_conditions).forEach(([conditionId, data]) => {
        if (data.has_condition === 'yes' && data.medication) {
          medications.push(data.medication);
        }
      });

      // Build health conditions array
      const health_conditions = [];
      Object.entries(formData.medical_conditions).forEach(([conditionId, data]) => {
        if (data.has_condition === 'yes') {
          // Find the condition label
          for (const category of Object.values(MEDICAL_CONDITIONS)) {
            const condition = category.conditions.find(c => c.id === conditionId);
            if (condition) {
              health_conditions.push(condition.label.toLowerCase());
              break;
            }
          }
        }
      });

      const payload = {
        age: parseInt(formData.age),
        state: formData.state,
        gender: formData.gender,
        smoker: formData.smoker,
        coverage_type: formData.coverage_type,
        desired_coverage: parseInt(formData.desired_coverage),
        health_conditions: health_conditions,
        medications: medications
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

  const saveCase = () => {
    const caseData = {
      id: 'case_' + Date.now(),
      createdAt: new Date().toISOString(),
      formData: formData,
      recommendations: recommendations,
      leftover: calculateLeftover()
    };

    const cases = [...savedCases, caseData];
    setSavedCases(cases);
    localStorage.setItem('savedCases', JSON.stringify(cases));

    alert('Case saved successfully!');
  };

  const loadSavedCases = () => {
    try {
      const saved = localStorage.getItem('savedCases');
      if (saved) {
        setSavedCases(JSON.parse(saved));
      }
    } catch (err) {
      console.error('Error loading saved cases:', err);
    }
  };

  const loadCase = (caseData) => {
    setFormData(caseData.formData);
    setRecommendations(caseData.recommendations);
    setActiveTab('quote');
  };

  const deleteCase = (caseId) => {
    if (window.confirm('Are you sure you want to delete this case?')) {
      const cases = savedCases.filter(c => c.id !== caseId);
      setSavedCases(cases);
      localStorage.setItem('savedCases', JSON.stringify(cases));
    }
  };

  const exportCasePDF = (caseData) => {
    const htmlContent = generateCaseHTML(caseData);
    const printWindow = window.open('', '_blank');
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => printWindow.print(), 300);
  };

  const generateCaseHTML = (caseData) => {
    const data = caseData.formData;
    const leftover = caseData.leftover || 0;

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Case Summary - ${data.first_name} ${data.last_name}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { color: #2563eb; }
          h2 { color: #1e40af; margin-top: 20px; }
          .section { margin-bottom: 20px; }
          ul { list-style: none; padding: 0; }
          li { padding: 5px 0; }
          strong { display: inline-block; min-width: 200px; }
        </style>
      </head>
      <body>
        <h1>Life Insurance Case Summary</h1>

        <div class="section">
          <h2>Client Information</h2>
          <ul>
            <li><strong>Name:</strong> ${data.first_name} ${data.last_name}</li>
            <li><strong>Email:</strong> ${data.email}</li>
            <li><strong>Phone:</strong> ${data.phone}</li>
            <li><strong>Age:</strong> ${data.age}</li>
            <li><strong>DOB:</strong> ${data.dob || 'N/A'}</li>
            <li><strong>State:</strong> ${data.state}</li>
            <li><strong>Gender:</strong> ${data.gender === 'M' ? 'Male' : 'Female'}</li>
            <li><strong>Height:</strong> ${data.height_ft}'${data.height_in}"</li>
            <li><strong>Weight:</strong> ${data.weight} lbs</li>
            <li><strong>Smoker:</strong> ${data.smoker ? 'Yes' : 'No'}</li>
          </ul>
        </div>

        <div class="section">
          <h2>Coverage Information</h2>
          <ul>
            <li><strong>Coverage Type:</strong> ${data.coverage_type}</li>
            <li><strong>Desired Coverage:</strong> $${parseInt(data.desired_coverage || 0).toLocaleString()}</li>
          </ul>
        </div>

        <div class="section">
          <h2>Financial Snapshot</h2>
          <ul>
            <li><strong>Monthly Income:</strong> $${parseFloat(data.monthly_income || 0).toLocaleString()}</li>
            <li><strong>Monthly Expenses:</strong> $${parseFloat(data.monthly_expenses || 0).toLocaleString()}</li>
            <li><strong>Leftover Monthly Funds:</strong> $${leftover.toLocaleString()}</li>
          </ul>
        </div>

        <div class="section">
          <h2>Medical Conditions</h2>
          <ul>
            ${Object.entries(data.medical_conditions || {})
              .filter(([_, cond]) => cond.has_condition === 'yes')
              .map(([id, cond]) => {
                let label = id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                return `<li><strong>${label}:</strong> ${cond.medication || 'N/A'} ${cond.year ? `(${cond.year})` : ''}</li>`;
              })
              .join('') || '<li>No conditions reported</li>'}
          </ul>
        </div>

        ${data.notes ? `
        <div class="section">
          <h2>Additional Notes</h2>
          <p>${data.notes}</p>
        </div>
        ` : ''}

        ${caseData.recommendations && caseData.recommendations.length > 0 ? `
        <div class="section">
          <h2>Recommended Carriers</h2>
          <ol>
            ${caseData.recommendations.map(rec => `
              <li>
                <strong>${rec.carrier} - ${rec.product}</strong><br>
                ${rec.reason}<br>
                Match: ${Math.round(rec.confidence * 100)}%
              </li>
            `).join('')}
          </ol>
        </div>
        ` : ''}

        <p style="margin-top: 40px; color: #6b7280; font-size: 12px;">
          Generated: ${new Date().toLocaleString()}<br>
          Powered by Insurance Carrier Predictor
        </p>
      </body>
      </html>
    `;
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      age: '',
      dob: '',
      state: 'TX',
      gender: 'M',
      height_ft: '',
      height_in: '',
      weight: '',
      smoker: false,
      coverage_type: 'Term',
      desired_coverage: '',
      monthly_income: '',
      monthly_expenses: '',
      medical_conditions: {},
      notes: ''
    });
    setRecommendations(null);
    setError(null);
  };

  const generateYearOptions = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = 0; i < 30; i++) {
      years.push(currentYear - i);
    }
    return years;
  };

  return (
    <div className="App">
      <div className="layout">
        <aside className="sidebar">
          <div className="sidebar-header">
            <h2>Navigation</h2>
          </div>
          <nav>
            <button
              className={`nav-item ${activeTab === 'quote' ? 'active' : ''}`}
              onClick={() => setActiveTab('quote')}
            >
              <span className="icon">🧮</span>
              <span>Quote Form</span>
            </button>
            <button
              className={`nav-item ${activeTab === 'saved' ? 'active' : ''}`}
              onClick={() => setActiveTab('saved')}
            >
              <span className="icon">💾</span>
              <span>Saved Cases ({savedCases.length})</span>
            </button>
          </nav>
        </aside>

        <main className="main-content">
          {activeTab === 'quote' ? (
            <div className="quote-tab">
              <header className="app-header">
                <div>
                  <h1>Life Insurance Quote & Case Builder</h1>
                  <p>Comprehensive intake tool for quoting, underwriting, and saving client cases</p>
                </div>
                <span className="badge badge-accent">AI-Powered</span>
              </header>

              <form onSubmit={handleSubmit} className="form-shell">
                {/* Client Contact Information */}
                <section className="form-section">
                  <h2 className="section-title">Client Contact Information</h2>
                  <p className="section-subtitle">Basic contact details and demographics</p>

                  <div className="form-grid-2">
                    <div className="form-field">
                      <label>First Name *</label>
                      <input
                        type="text"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleInputChange}
                        required
                      />
                    </div>

                    <div className="form-field">
                      <label>Last Name *</label>
                      <input
                        type="text"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleInputChange}
                        required
                      />
                    </div>

                    <div className="form-field">
                      <label>Email *</label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                      />
                    </div>

                    <div className="form-field">
                      <label>Phone *</label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        required
                        placeholder="(555) 123-4567"
                      />
                    </div>

                    <div className="form-field">
                      <label>State *</label>
                      <select name="state" value={formData.state} onChange={handleInputChange} required>
                        {US_STATES.map(state => (
                          <option key={state} value={state}>{state}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </section>

                {/* Coverage Information */}
                <section className="form-section">
                  <h2 className="section-title">Coverage Information</h2>
                  <p className="section-subtitle">Desired protection and structure</p>

                  <div className="form-grid-2">
                    <div className="form-field">
                      <label>Coverage Type *</label>
                      <select name="coverage_type" value={formData.coverage_type} onChange={handleInputChange} required>
                        <option value="Term">Term Life</option>
                        <option value="Whole Life">Whole Life</option>
                        <option value="IUL">Indexed Universal Life</option>
                        <option value="Final Expense">Final Expense</option>
                        <option value="Universal Life">Universal Life</option>
                      </select>
                    </div>

                    <div className="form-field">
                      <label>Face Amount ($) *</label>
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
                      <span className="hint">Target death benefit in dollars</span>
                    </div>

                    <div className="form-field">
                      <label>Age *</label>
                      <input
                        type="number"
                        name="age"
                        value={formData.age}
                        onChange={handleInputChange}
                        required
                        min="0"
                        max="120"
                      />
                    </div>

                    <div className="form-field">
                      <label>Date of Birth</label>
                      <input
                        type="date"
                        name="dob"
                        value={formData.dob}
                        onChange={handleInputChange}
                      />
                      <span className="hint">Age will auto-calculate from DOB</span>
                    </div>

                    <div className="form-field">
                      <label>Gender *</label>
                      <select name="gender" value={formData.gender} onChange={handleInputChange} required>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                      </select>
                    </div>

                    <div className="form-field">
                      <label>Height & Weight *</label>
                      <div className="input-group">
                        <input
                          type="number"
                          name="height_ft"
                          value={formData.height_ft}
                          onChange={handleInputChange}
                          placeholder="ft"
                          min="3"
                          max="8"
                          required
                          style={{ width: '70px' }}
                        />
                        <input
                          type="number"
                          name="height_in"
                          value={formData.height_in}
                          onChange={handleInputChange}
                          placeholder="in"
                          min="0"
                          max="11"
                          required
                          style={{ width: '70px' }}
                        />
                        <input
                          type="number"
                          name="weight"
                          value={formData.weight}
                          onChange={handleInputChange}
                          placeholder="lbs"
                          min="50"
                          max="600"
                          required
                          style={{ width: '100px' }}
                        />
                      </div>
                    </div>

                    <div className="form-field checkbox-field">
                      <label>
                        <input
                          type="checkbox"
                          name="smoker"
                          checked={formData.smoker}
                          onChange={handleInputChange}
                        />
                        <span>Tobacco User</span>
                      </label>
                    </div>
                  </div>
                </section>

                {/* Financial Information */}
                <section className="form-section">
                  <h2 className="section-title">Financial Snapshot</h2>
                  <p className="section-subtitle">Quick snapshot for suitability and budgeting</p>

                  <div className="form-grid-2">
                    <div className="form-field">
                      <label>Monthly Income</label>
                      <input
                        type="number"
                        name="monthly_income"
                        value={formData.monthly_income}
                        onChange={handleInputChange}
                        placeholder="4000"
                        min="0"
                        step="100"
                      />
                    </div>

                    <div className="form-field">
                      <label>Monthly Expenses</label>
                      <input
                        type="number"
                        name="monthly_expenses"
                        value={formData.monthly_expenses}
                        onChange={handleInputChange}
                        placeholder="2500"
                        min="0"
                        step="100"
                      />
                    </div>
                  </div>

                  {(formData.monthly_income || formData.monthly_expenses) && (
                    <div className="leftover-display">
                      💰 Estimated leftover monthly funds:
                      <span className="value"> ${calculateLeftover().toLocaleString()}</span>
                    </div>
                  )}
                </section>

                {/* Medical Underwriting */}
                <section className="form-section">
                  <h2 className="section-title">Medical Underwriting</h2>
                  <p className="section-subtitle">Select conditions and medications if applicable</p>

                  <div className="medical-categories">
                    {Object.entries(MEDICAL_CONDITIONS).map(([categoryKey, category]) => (
                      <div key={categoryKey} className={`medical-category ${expandedCategories[categoryKey] ? 'open' : ''}`}>
                        <div className="category-header" onClick={() => toggleCategory(categoryKey)}>
                          <h3>
                            <span className="icon">{category.icon}</span>
                            {category.title}
                          </h3>
                          <span className="toggle-icon">{expandedCategories[categoryKey] ? '▼' : '▶'}</span>
                        </div>

                        {expandedCategories[categoryKey] && (
                          <div className="category-body">
                            {category.conditions.map(condition => (
                              <div key={condition.id} className="condition-row">
                                <div className="condition-question">
                                  <label className="condition-label">{condition.label}?</label>
                                  <div className="radio-group">
                                    <label>
                                      <input
                                        type="radio"
                                        name={`${condition.id}_radio`}
                                        value="yes"
                                        checked={formData.medical_conditions[condition.id]?.has_condition === 'yes'}
                                        onChange={() => handleMedicalConditionChange(condition.id, 'has_condition', 'yes')}
                                      />
                                      Yes
                                    </label>
                                    <label>
                                      <input
                                        type="radio"
                                        name={`${condition.id}_radio`}
                                        value="no"
                                        checked={formData.medical_conditions[condition.id]?.has_condition === 'no'}
                                        onChange={() => handleMedicalConditionChange(condition.id, 'has_condition', 'no')}
                                      />
                                      No
                                    </label>
                                  </div>
                                </div>

                                {formData.medical_conditions[condition.id]?.has_condition === 'yes' && (
                                  <div className="condition-details">
                                    <select
                                      value={formData.medical_conditions[condition.id]?.medication || ''}
                                      onChange={(e) => handleMedicalConditionChange(condition.id, 'medication', e.target.value)}
                                      className="med-select"
                                    >
                                      <option value="">Select Medication</option>
                                      {condition.meds.map(med => (
                                        <option key={med} value={med}>{med}</option>
                                      ))}
                                    </select>

                                    <select
                                      value={formData.medical_conditions[condition.id]?.year || ''}
                                      onChange={(e) => handleMedicalConditionChange(condition.id, 'year', e.target.value)}
                                      className="year-select"
                                    >
                                      <option value="">Year Diagnosed</option>
                                      {generateYearOptions().map(year => (
                                        <option key={year} value={year}>{year}</option>
                                      ))}
                                    </select>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>

                {/* Additional Notes */}
                <section className="form-section">
                  <h2 className="section-title">Additional Information</h2>
                  <div className="form-field">
                    <label>Notes / Additional Health Info</label>
                    <textarea
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      placeholder="List any surgeries, extra diagnoses, or underwriting notes..."
                      rows="4"
                    />
                  </div>
                </section>

                {/* Action Buttons */}
                <div className="button-row">
                  <button type="submit" className="btn-primary" disabled={loading}>
                    {loading ? 'Finding Carriers...' : 'Get Quote'}
                  </button>
                  <button type="button" className="btn-secondary" onClick={resetForm}>
                    Reset Form
                  </button>
                  {recommendations && (
                    <button type="button" className="btn-secondary" onClick={saveCase}>
                      Save Case
                    </button>
                  )}
                </div>

                {/* Error Display */}
                {error && (
                  <div className="error-card">
                    <h3>⚠️ Error</h3>
                    <p>{error}</p>
                  </div>
                )}

                {/* Results Display */}
                {recommendations && recommendations.length > 0 && (
                  <div className="results-card">
                    <h2>📊 Recommended Carriers</h2>
                    <div className="results-summary">
                      Profile: Age {formData.age}, {formData.smoker ? 'tobacco' : 'non-tobacco'},
                      {formData.coverage_type}, ${parseInt(formData.desired_coverage).toLocaleString()} coverage
                    </div>
                    <div className="recommendations-grid">
                      {recommendations.map((rec, index) => (
                        <div key={index} className="recommendation-card">
                          <div className="rec-header">
                            <div>
                              <h3>{rec.carrier}</h3>
                              <p className="product-name">{rec.product}</p>
                            </div>
                            <span className="confidence-badge">
                              {Math.round(rec.confidence * 100)}% Match
                            </span>
                          </div>
                          <div className="rec-body">
                            <p className="reason">{rec.reason}</p>
                            {rec.portal_url && (
                              <a
                                href={rec.portal_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="portal-link"
                              >
                                Go to Agent Portal →
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
              </form>
            </div>
          ) : (
            <div className="saved-tab">
              <header className="app-header">
                <div>
                  <h1>Saved Cases</h1>
                  <p>Access previously saved client cases and generate reports</p>
                </div>
                <span className="badge">Local Storage</span>
              </header>

              <div className="saved-cases-container">
                {savedCases.length === 0 ? (
                  <div className="no-results-card">
                    <h3>No Saved Cases</h3>
                    <p>Complete a quote and save it to see it here.</p>
                  </div>
                ) : (
                  <div className="saved-cases-list">
                    {savedCases.map(caseData => {
                      const data = caseData.formData;
                      return (
                        <div key={caseData.id} className="saved-case-item">
                          <div className="case-meta">
                            <h3>{data.first_name} {data.last_name}</h3>
                            <p className="case-detail">
                              {new Date(caseData.createdAt).toLocaleDateString()} •
                              ${parseInt(data.desired_coverage || 0).toLocaleString()} •
                              {data.coverage_type}
                            </p>
                            <p className="case-detail">
                              Age {data.age} • {data.state}
                            </p>
                          </div>
                          <div className="case-actions">
                            <button
                              className="btn-secondary btn-sm"
                              onClick={() => loadCase(caseData)}
                            >
                              Load
                            </button>
                            <button
                              className="btn-secondary btn-sm"
                              onClick={() => exportCasePDF(caseData)}
                            >
                              Export PDF
                            </button>
                            <button
                              className="btn-danger btn-sm"
                              onClick={() => deleteCase(caseData.id)}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
