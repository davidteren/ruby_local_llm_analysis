import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import glob

def load_test_results(file_paths):
    results = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data = json.load(f)
            model_name = data['metadata']['model']['identifier']
            results.append({
                'file_path': file_path,
                'model_name': model_name,
                'data': data
            })
    return results

def create_performance_df(results):
    performance_data = []
    for result in results:
        model_name = result['model_name']
        for test in result['data']['tests']:
            performance_data.append({
                'Model': model_name,
                'Test': test['test_name'],
                'Time (s)': test['time_taken'],
                'Total Tokens': test['tokens']['total_tokens'],
                'Response Length': len(test['response'])
            })
    return pd.DataFrame(performance_data)

def get_quality_scores():
    return {
        'Basic Ruby Understanding': {'mistral-nemo-instruct-2407': 9, 'nuprl_-_multipl-t-starcoderbase_1b': 5},
        'Code Implementation': {'mistral-nemo-instruct-2407': 9, 'nuprl_-_multipl-t-starcoderbase_1b': 4},
        'Error Handling': {'mistral-nemo-instruct-2407': 9, 'nuprl_-_multipl-t-starcoderbase_1b': 2},
        'Ruby Best Practices': {'mistral-nemo-instruct-2407': 9, 'nuprl_-_multipl-t-starcoderbase_1b': 5},
        'Advanced Ruby Features': {'mistral-nemo-instruct-2407': 9, 'nuprl_-_multipl-t-starcoderbase_1b': 2}
    }

def create_quality_df(quality_scores):
    quality_data = []
    for test, scores in quality_scores.items():
        for model, score in scores.items():
            quality_data.append({
                'Test': test,
                'Model': model,
                'Quality Score': score
            })
    return pd.DataFrame(quality_data)

def main():
    st.set_page_config(page_title="LLM Model Analysis", layout="wide")
    
    st.title("LLM Model Analysis Dashboard")
    
    # Load test results
    json_files = glob.glob('*.json')
    if not json_files:
        st.error("No JSON result files found in the current directory.")
        return
        
    results = load_test_results(json_files)
    performance_df = create_performance_df(results)
    quality_df = create_quality_df(get_quality_scores())
    
    # Model Overview
    st.header("Model Overview")
    cols = st.columns(len(results))
    for idx, result in enumerate(results):
        with cols[idx]:
            st.subheader(result['model_name'])
            st.metric("Model Size", result['data']['metadata']['model']['size'])
            st.metric("Total Time", f"{result['data']['metadata']['total_time_taken']:.2f}s")
            st.metric("Total Tokens", result['data']['metadata']['total_tokens_used'])
            memory_gb = result['data']['metadata']['system']['memory_available'] / (1024**3)
            st.metric("Memory Available", f"{memory_gb:.2f} GB")

    # Tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["Performance Analysis", "Accuracy Analysis", "Response Comparison"])
    
    with tab1:
        st.subheader("Performance Analysis")
        
        # Response Time Comparison
        fig_time = px.bar(
            performance_df,
            x='Test',
            y='Time (s)',
            color='Model',
            barmode='group',
            title='Response Time Comparison'
        )
        fig_time.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Token Usage Comparison
        fig_tokens = px.bar(
            performance_df,
            x='Test',
            y='Total Tokens',
            color='Model',
            barmode='group',
            title='Token Usage Comparison'
        )
        fig_tokens.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_tokens, use_container_width=True)
        
    with tab2:
        st.subheader("Accuracy Analysis")
        
        # Quality Score Comparison
        fig_quality = px.bar(
            quality_df,
            x='Test',
            y='Quality Score',
            color='Model',
            barmode='group',
            title='Quality Score Comparison'
        )
        fig_quality.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_quality, use_container_width=True)
        
        # Detailed quality scores
        st.subheader("Detailed Quality Scores")
        for test in quality_df['Test'].unique():
            test_scores = quality_df[quality_df['Test'] == test]
            cols = st.columns(len(results))
            for idx, (_, row) in enumerate(test_scores.iterrows()):
                with cols[idx]:
                    st.metric(
                        f"{row['Model']}",
                        f"{row['Quality Score']}/10"
                    )
    
    with tab3:
        st.subheader("Response Comparison")
        
        # Test selection
        selected_test = st.selectbox(
            "Select Test Case",
            options=performance_df['Test'].unique()
        )
        
        # Display responses
        cols = st.columns(len(results))
        for idx, result in enumerate(results):
            with cols[idx]:
                st.subheader(result['model_name'])
                test_response = next(
                    test['response'] 
                    for test in result['data']['tests'] 
                    if test['test_name'] == selected_test
                )
                st.text_area(
                    "Response",
                    value=test_response,
                    height=400,
                    key=f"response_{idx}"
                )

if __name__ == "__main__":
    main()
