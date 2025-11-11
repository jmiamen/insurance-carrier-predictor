# Smart Health Questionnaire Design

## 🎯 Current Pattern (From Screenshot Analysis)

### How It Works
1. **Dropdown selector**: "Select health condition..."
2. **Conditional questions appear**: Based on selected condition
3. **Answers get logged**: Added to list below
4. **Repeat for multiple conditions**: Clean, no clutter
5. **Final summary**: All conditions + details in compact format

---

## 📋 Condition-Specific Questionnaires

### Diabetes
**Follow-up Questions:**
```
1. Type: [ ] Type 1  [ ] Type 2  [ ] Gestational
2. Diagnosed: [Date picker] (YYYY-MM)
3. Current A1C: [____] %
4. Current medications: [Dropdown: Metformin, Insulin, Januvia, etc.]
5. Complications: [ ] Retinopathy [ ] Neuropathy [ ] Nephropathy [ ] None
6. Controlled? [ ] Yes, stable [ ] No, unstable
```

**Output to List:**
```
✓ Diabetes - Type 2, diagnosed 2018, A1C 6.5%, Metformin, no complications, controlled
```

---

### High Blood Pressure
**Follow-up Questions:**
```
1. Diagnosed: [Date picker] (YYYY-MM)
2. Current reading: [___]/[___] mmHg
3. Medications: [Dropdown: Lisinopril, Amlodipine, Losartan, etc.]
4. Last elevated reading: [Date picker]
5. Hospitalized? [ ] Yes (when: ___) [ ] No
```

**Output to List:**
```
✓ High Blood Pressure - Diagnosed 2019, 130/85 mmHg, Lisinopril 10mg, controlled, no hospitalizations
```

---

### High Cholesterol
**Follow-up Questions:**
```
1. Total cholesterol: [____] mg/dL
2. LDL: [____] mg/dL
3. HDL: [____] mg/dL
4. Triglycerides: [____] mg/dL
5. Medications: [Dropdown: Lipitor, Crestor, Zocor, etc.]
6. Last lab date: [Date picker]
```

**Output to List:**
```
✓ High Cholesterol - Total 210, LDL 130, HDL 50, Lipitor 20mg, last lab 2024-09
```

---

### Heart Disease / Cardiac History
**Follow-up Questions:**
```
1. Condition: [ ] Heart attack [ ] Bypass surgery [ ] Stent [ ] Angina [ ] Other: ___
2. Date of event: [Date picker]
3. Current symptoms: [ ] Chest pain [ ] Shortness of breath [ ] None
4. Medications: [Multi-select: Beta blockers, ACE inhibitors, Blood thinners, etc.]
5. Last stress test: [Date picker]
6. Cleared by cardiologist? [ ] Yes [ ] No
```

**Output to List:**
```
✓ Heart Disease - Stent placed 2020, no current symptoms, on Plavix + Carvedilol, stress test clear 2024-06
```

---

### Cancer
**Follow-up Questions:**
```
1. Type: [Text input]
2. Stage at diagnosis: [ ] Stage 0 [ ] Stage I [ ] Stage II [ ] Stage III [ ] Stage IV
3. Date diagnosed: [Date picker]
4. Treatment: [ ] Surgery [ ] Chemo [ ] Radiation [ ] Immunotherapy
5. Treatment completion date: [Date picker]
6. Current status: [ ] Remission [ ] NED (No Evidence of Disease) [ ] Recurrence [ ] Ongoing treatment
7. Last oncologist visit: [Date picker]
```

**Output to List:**
```
✓ Cancer - Breast cancer Stage I, diagnosed 2019, surgery + radiation, NED since 2020-03, last check 2024-10
```

---

### COPD / Asthma
**Follow-up Questions:**
```
1. Condition: [ ] Asthma [ ] COPD [ ] Emphysema [ ] Chronic bronchitis
2. Severity: [ ] Mild (no daily symptoms) [ ] Moderate (daily controller) [ ] Severe (hospitalization history)
3. Oxygen use: [ ] Yes [ ] No
4. Hospitalizations in last 2 years: [Number]
5. Current medications: [Multi-select: Inhalers, steroids, etc.]
6. Last pulmonary function test: [Date picker]
```

**Output to List:**
```
✓ Asthma - Mild, no hospitalizations, rescue inhaler only, no oxygen, last PFT 2024-08
```

---

### Kidney Disease
**Follow-up Questions:**
```
1. Stage: [ ] Stage 1 [ ] Stage 2 [ ] Stage 3 [ ] Stage 4 [ ] Stage 5 / Dialysis
2. eGFR: [____] mL/min
3. Creatinine: [____] mg/dL
4. Dialysis: [ ] Yes, hemodialysis [ ] Yes, peritoneal [ ] No
5. Kidney transplant: [ ] Yes (date: ___) [ ] No
6. Cause: [ ] Diabetes [ ] Hypertension [ ] Unknown [ ] Other: ___
```

**Output to List:**
```
✓ Kidney Disease - Stage 2, eGFR 75, creatinine 1.2, no dialysis, cause: hypertension
```

---

### Mental Health
**Follow-up Questions:**
```
1. Condition: [ ] Depression [ ] Anxiety [ ] Bipolar [ ] PTSD [ ] Other: ___
2. Diagnosed: [Date picker]
3. Current medications: [Multi-select: SSRIs, SNRIs, etc.]
4. Hospitalizations/ER visits: [ ] Yes (when: ___) [ ] No
5. Currently stable: [ ] Yes [ ] No
6. Last therapist/psychiatrist visit: [Date picker]
```

**Output to List:**
```
✓ Depression - Diagnosed 2018, on Lexapro 10mg, no hospitalizations, stable, last visit 2024-09
```

---

### Sleep Apnea
**Follow-up Questions:**
```
1. Severity: [ ] Mild [ ] Moderate [ ] Severe
2. AHI score: [____] events/hour
3. Treatment: [ ] CPAP [ ] BiPAP [ ] None [ ] Surgery
4. Compliant with CPAP: [ ] Yes (___+ hours/night) [ ] No
5. Last sleep study: [Date picker]
```

**Output to List:**
```
✓ Sleep Apnea - Moderate, AHI 22, CPAP compliant 7+ hrs/night, last study 2024-01
```

---

## 🎨 UI Component Design

### Health Condition Selector Component

```jsx
import React, { useState } from 'react';

const HealthQuestionnaireBuilder = () => {
  const [conditions, setConditions] = useState([]);
  const [selectedCondition, setSelectedCondition] = useState('');
  const [questionnaire, setQuestionnaire] = useState(null);

  const conditionTemplates = {
    diabetes: {
      name: 'Diabetes',
      questions: [
        { id: 'type', type: 'radio', label: 'Type', options: ['Type 1', 'Type 2', 'Gestational'] },
        { id: 'diagnosed', type: 'date', label: 'Diagnosed date' },
        { id: 'a1c', type: 'number', label: 'Current A1C (%)', step: 0.1 },
        { id: 'medications', type: 'select', label: 'Medications', options: ['Metformin', 'Insulin', 'Januvia', 'Jardiance', 'Other'] },
        { id: 'complications', type: 'checkbox', label: 'Complications', options: ['Retinopathy', 'Neuropathy', 'Nephropathy', 'None'] },
        { id: 'controlled', type: 'radio', label: 'Controlled?', options: ['Yes, stable', 'No, unstable'] }
      ]
    },
    hypertension: {
      name: 'High Blood Pressure',
      questions: [
        { id: 'diagnosed', type: 'date', label: 'Diagnosed date' },
        { id: 'systolic', type: 'number', label: 'Current systolic (mmHg)' },
        { id: 'diastolic', type: 'number', label: 'Current diastolic (mmHg)' },
        { id: 'medications', type: 'select', label: 'Medications', options: ['Lisinopril', 'Amlodipine', 'Losartan', 'Metoprolol', 'Other'] },
        { id: 'hospitalized', type: 'radio', label: 'Hospitalized?', options: ['Yes', 'No'] }
      ]
    },
    cholesterol: {
      name: 'High Cholesterol',
      questions: [
        { id: 'total', type: 'number', label: 'Total cholesterol (mg/dL)' },
        { id: 'ldl', type: 'number', label: 'LDL (mg/dL)' },
        { id: 'hdl', type: 'number', label: 'HDL (mg/dL)' },
        { id: 'triglycerides', type: 'number', label: 'Triglycerides (mg/dL)' },
        { id: 'medications', type: 'select', label: 'Medications', options: ['Lipitor', 'Crestor', 'Zocor', 'Pravastatin', 'Other'] },
        { id: 'lastLab', type: 'date', label: 'Last lab date' }
      ]
    },
    heartDisease: {
      name: 'Heart Disease',
      questions: [
        { id: 'type', type: 'radio', label: 'Condition', options: ['Heart attack', 'Bypass surgery', 'Stent', 'Angina', 'Other'] },
        { id: 'eventDate', type: 'date', label: 'Date of event' },
        { id: 'symptoms', type: 'checkbox', label: 'Current symptoms', options: ['Chest pain', 'Shortness of breath', 'None'] },
        { id: 'medications', type: 'multiselect', label: 'Medications', options: ['Beta blockers', 'ACE inhibitors', 'Blood thinners', 'Statins'] },
        { id: 'lastStressTest', type: 'date', label: 'Last stress test' },
        { id: 'cleared', type: 'radio', label: 'Cleared by cardiologist?', options: ['Yes', 'No'] }
      ]
    },
    cancer: {
      name: 'Cancer',
      questions: [
        { id: 'type', type: 'text', label: 'Type of cancer' },
        { id: 'stage', type: 'radio', label: 'Stage at diagnosis', options: ['Stage 0', 'Stage I', 'Stage II', 'Stage III', 'Stage IV'] },
        { id: 'diagnosed', type: 'date', label: 'Date diagnosed' },
        { id: 'treatment', type: 'checkbox', label: 'Treatment', options: ['Surgery', 'Chemotherapy', 'Radiation', 'Immunotherapy'] },
        { id: 'completionDate', type: 'date', label: 'Treatment completion date' },
        { id: 'status', type: 'radio', label: 'Current status', options: ['Remission', 'NED', 'Recurrence', 'Ongoing treatment'] },
        { id: 'lastVisit', type: 'date', label: 'Last oncologist visit' }
      ]
    },
    copdAsthma: {
      name: 'COPD / Asthma',
      questions: [
        { id: 'type', type: 'radio', label: 'Condition', options: ['Asthma', 'COPD', 'Emphysema', 'Chronic bronchitis'] },
        { id: 'severity', type: 'radio', label: 'Severity', options: ['Mild', 'Moderate', 'Severe'] },
        { id: 'oxygen', type: 'radio', label: 'Oxygen use', options: ['Yes', 'No'] },
        { id: 'hospitalizations', type: 'number', label: 'Hospitalizations in last 2 years' },
        { id: 'medications', type: 'text', label: 'Current medications' },
        { id: 'lastPFT', type: 'date', label: 'Last pulmonary function test' }
      ]
    },
    kidneyDisease: {
      name: 'Kidney Disease',
      questions: [
        { id: 'stage', type: 'radio', label: 'Stage', options: ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5 / Dialysis'] },
        { id: 'egfr', type: 'number', label: 'eGFR (mL/min)' },
        { id: 'creatinine', type: 'number', label: 'Creatinine (mg/dL)', step: 0.1 },
        { id: 'dialysis', type: 'radio', label: 'Dialysis', options: ['Yes, hemodialysis', 'Yes, peritoneal', 'No'] },
        { id: 'transplant', type: 'radio', label: 'Kidney transplant', options: ['Yes', 'No'] },
        { id: 'cause', type: 'radio', label: 'Cause', options: ['Diabetes', 'Hypertension', 'Unknown', 'Other'] }
      ]
    },
    mentalHealth: {
      name: 'Mental Health',
      questions: [
        { id: 'type', type: 'radio', label: 'Condition', options: ['Depression', 'Anxiety', 'Bipolar', 'PTSD', 'Other'] },
        { id: 'diagnosed', type: 'date', label: 'Diagnosed date' },
        { id: 'medications', type: 'text', label: 'Current medications' },
        { id: 'hospitalized', type: 'radio', label: 'Hospitalizations/ER visits', options: ['Yes', 'No'] },
        { id: 'stable', type: 'radio', label: 'Currently stable', options: ['Yes', 'No'] },
        { id: 'lastVisit', type: 'date', label: 'Last therapist/psychiatrist visit' }
      ]
    },
    sleepApnea: {
      name: 'Sleep Apnea',
      questions: [
        { id: 'severity', type: 'radio', label: 'Severity', options: ['Mild', 'Moderate', 'Severe'] },
        { id: 'ahi', type: 'number', label: 'AHI score (events/hour)' },
        { id: 'treatment', type: 'radio', label: 'Treatment', options: ['CPAP', 'BiPAP', 'None', 'Surgery'] },
        { id: 'compliant', type: 'radio', label: 'Compliant with CPAP', options: ['Yes', 'No'] },
        { id: 'hours', type: 'number', label: 'Hours per night (if CPAP)', step: 0.5 },
        { id: 'lastStudy', type: 'date', label: 'Last sleep study' }
      ]
    }
  };

  const handleConditionSelect = (conditionKey) => {
    setSelectedCondition(conditionKey);
    setQuestionnaire(conditionTemplates[conditionKey]);
  };

  const handleSubmitQuestionnaire = (answers) => {
    const summary = generateSummary(questionnaire.name, answers);
    setConditions([...conditions, { condition: questionnaire.name, summary, answers }]);
    setSelectedCondition('');
    setQuestionnaire(null);
  };

  const generateSummary = (conditionName, answers) => {
    // Logic to generate human-readable summary
    // e.g., "Diabetes - Type 2, diagnosed 2018, A1C 6.5%, Metformin, no complications, controlled"
    return `${conditionName} - ${Object.values(answers).join(', ')}`;
  };

  return (
    <div className="health-questionnaire-builder">
      <h3>Health Conditions</h3>

      {/* Condition Selector */}
      <div className="condition-selector">
        <label>Select health condition:</label>
        <select value={selectedCondition} onChange={(e) => handleConditionSelect(e.target.value)}>
          <option value="">-- Select condition --</option>
          <option value="diabetes">Diabetes</option>
          <option value="hypertension">High Blood Pressure</option>
          <option value="cholesterol">High Cholesterol</option>
          <option value="heartDisease">Heart Disease</option>
          <option value="cancer">Cancer</option>
          <option value="copdAsthma">COPD / Asthma</option>
          <option value="kidneyDisease">Kidney Disease</option>
          <option value="mentalHealth">Mental Health</option>
          <option value="sleepApnea">Sleep Apnea</option>
        </select>
      </div>

      {/* Dynamic Questionnaire */}
      {questionnaire && (
        <QuestionnaireForm
          questionnaire={questionnaire}
          onSubmit={handleSubmitQuestionnaire}
          onCancel={() => { setSelectedCondition(''); setQuestionnaire(null); }}
        />
      )}

      {/* Added Conditions List */}
      <div className="conditions-list">
        <h4>Added Conditions:</h4>
        {conditions.length === 0 && (
          <p className="empty-state">No conditions added yet</p>
        )}
        {conditions.map((cond, index) => (
          <div key={index} className="condition-item">
            <span className="check-icon">✓</span>
            <span className="condition-summary">{cond.summary}</span>
            <button className="btn-remove" onClick={() => removeCondition(index)}>
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

const QuestionnaireForm = ({ questionnaire, onSubmit, onCancel }) => {
  const [answers, setAnswers] = useState({});

  const handleChange = (questionId, value) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(answers);
  };

  return (
    <div className="questionnaire-form">
      <h4>{questionnaire.name} Details</h4>
      <form onSubmit={handleSubmit}>
        {questionnaire.questions.map((q) => (
          <div key={q.id} className="form-group">
            <label>{q.label}</label>
            {q.type === 'radio' && (
              <div className="radio-group">
                {q.options.map((opt) => (
                  <label key={opt} className="radio-option">
                    <input
                      type="radio"
                      name={q.id}
                      value={opt}
                      onChange={(e) => handleChange(q.id, e.target.value)}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            )}
            {q.type === 'checkbox' && (
              <div className="checkbox-group">
                {q.options.map((opt) => (
                  <label key={opt} className="checkbox-option">
                    <input
                      type="checkbox"
                      value={opt}
                      onChange={(e) => {
                        const checked = answers[q.id] || [];
                        if (e.target.checked) {
                          handleChange(q.id, [...checked, opt]);
                        } else {
                          handleChange(q.id, checked.filter(v => v !== opt));
                        }
                      }}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            )}
            {q.type === 'text' && (
              <input
                type="text"
                onChange={(e) => handleChange(q.id, e.target.value)}
              />
            )}
            {q.type === 'number' && (
              <input
                type="number"
                step={q.step || 1}
                onChange={(e) => handleChange(q.id, e.target.value)}
              />
            )}
            {q.type === 'date' && (
              <input
                type="month"
                onChange={(e) => handleChange(q.id, e.target.value)}
              />
            )}
            {q.type === 'select' && (
              <select onChange={(e) => handleChange(q.id, e.target.value)}>
                <option value="">-- Select --</option>
                {q.options.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            )}
          </div>
        ))}

        <div className="form-actions">
          <button type="submit" className="btn-primary">Add Condition</button>
          <button type="button" className="btn-secondary" onClick={onCancel}>Cancel</button>
        </div>
      </form>
    </div>
  );
};

export default HealthQuestionnaireBuilder;
```

---

## 📊 Example Output Format

### What Agent Sees (Compact List)
```
Health Conditions:
✓ Diabetes - Type 2, diagnosed 2018, A1C 6.5%, Metformin, no complications, controlled
✓ High Blood Pressure - Diagnosed 2019, 130/85 mmHg, Lisinopril 10mg, no hospitalizations
✓ High Cholesterol - Total 210, LDL 130, HDL 50, Lipitor 20mg, last lab 2024-09
```

### What API Receives (Structured Data)
```json
{
  "health_conditions": [
    {
      "condition": "Diabetes",
      "type": "Type 2",
      "diagnosed": "2018-01",
      "a1c": 6.5,
      "medications": "Metformin",
      "complications": ["None"],
      "controlled": "Yes, stable"
    },
    {
      "condition": "High Blood Pressure",
      "diagnosed": "2019-06",
      "systolic": 130,
      "diastolic": 85,
      "medications": "Lisinopril",
      "hospitalized": "No"
    },
    {
      "condition": "High Cholesterol",
      "total": 210,
      "ldl": 130,
      "hdl": 50,
      "triglycerides": 150,
      "medications": "Lipitor",
      "lastLab": "2024-09"
    }
  ]
}
```

---

## 🎨 CSS Styling

```css
.health-questionnaire-builder {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.condition-selector {
  margin-bottom: 24px;
}

.condition-selector select {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  background: white;
}

.questionnaire-form {
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #374151;
}

.radio-group,
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-option,
.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 400;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary {
  background: #7c3aed;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary {
  background: white;
  color: #374151;
  padding: 12px 24px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.conditions-list {
  margin-top: 24px;
}

.conditions-list h4 {
  margin-bottom: 16px;
  color: #111827;
}

.condition-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 6px;
  margin-bottom: 8px;
}

.check-icon {
  color: #16a34a;
  font-size: 18px;
  font-weight: bold;
}

.condition-summary {
  flex: 1;
  color: #166534;
  font-size: 14px;
}

.btn-remove {
  background: transparent;
  color: #dc2626;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 4px 8px;
}

.empty-state {
  color: #9ca3af;
  font-style: italic;
  padding: 12px;
}
```

---

## 🚀 Benefits Over File Upload

| Feature | File Upload | Smart Questionnaire |
|---------|-------------|---------------------|
| **Data Structure** | Unstructured text/PDF | Structured JSON |
| **Processing** | Requires OCR/parsing | Ready to use |
| **Accuracy** | Depends on document quality | Validated input |
| **Agent Control** | Limited (depends on docs) | Full control of narrative |
| **Underwriting** | Manual review needed | Auto-matched to rules |
| **UI Cleanliness** | File list can be messy | Compact summaries |
| **Mobile Friendly** | File pickers are awkward | Forms work great |
| **Validation** | Hard to validate | Built-in validation |

---

## ✅ Implementation Priority

1. **Phase 1: Core Conditions** (Week 1)
   - Diabetes
   - High blood pressure
   - High cholesterol
   - These cover 80% of cases

2. **Phase 2: Advanced Conditions** (Week 2)
   - Heart disease
   - Cancer
   - COPD/Asthma
   - Sleep apnea

3. **Phase 3: Edge Cases** (Week 3)
   - Kidney disease
   - Mental health
   - Other rare conditions
   - Custom "Other" condition with free text

---

## 🎯 Success Metrics

- **Completion Rate:** % of agents who add health details
- **Accuracy:** % of recommendations that match added conditions
- **Time Saved:** Minutes saved vs manual entry
- **Agent Satisfaction:** Survey score improvement

**Expected Impact:**
- 90%+ structured data (vs 30% with file upload)
- 50% faster than manual text entry
- 95%+ accuracy for underwriting rules matching
