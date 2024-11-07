#! /usr/bin/env python3

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import glob

# Configure page settings
st.set_page_config(
    page_title="💎 RubyMojo - Local LLM Benchmarks",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply dark theme styling
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #0E1117;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1E2127;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            color: #FAFAFA;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2E3137;
        }
        .stMetric {
            background-color: #1E2127;
            padding: 15px;
            border-radius: 5px;
        }
        div[data-testid="stMetricValue"] {
            font-size: 24px;
            color: #00A4EF;
        }
        .plot-container {
            background-color: #1E2127 !important;
            border-radius: 5px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

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
    """Get quality scores for all models."""
    return {
        'Basic Ruby Understanding': {
            'mistral-nemo-instruct-2407': 9,
            'nuprl_-_multipl-t-starcoderbase_1b': 5,
            'qwen2.5-coder-7b-instruct': 8,
            'smollm2-360m-instruct': 6
        },
        'Code Implementation': {
            'mistral-nemo-instruct-2407': 9,
            'nuprl_-_multipl-t-starcoderbase_1b': 4,
            'qwen2.5-coder-7b-instruct': 8,
            'smollm2-360m-instruct': 5
        },
        'Error Handling': {
            'mistral-nemo-instruct-2407': 9,
            'nuprl_-_multipl-t-starcoderbase_1b': 2,
            'qwen2.5-coder-7b-instruct': 8,
            'smollm2-360m-instruct': 3
        },
        'Ruby Best Practices': {
            'mistral-nemo-instruct-2407': 9,
            'nuprl_-_multipl-t-starcoderbase_1b': 5,
            'qwen2.5-coder-7b-instruct': 8,
            'smollm2-360m-instruct': 6
        },
        'Advanced Ruby Features': {
            'mistral-nemo-instruct-2407': 9,
            'nuprl_-_multipl-t-starcoderbase_1b': 2,
            'qwen2.5-coder-7b-instruct': 8,
            'smollm2-360m-instruct': 4
        }
    }

def create_quality_df(quality_scores):
    """Create a DataFrame from quality scores."""
    quality_data = []
    for test, scores in quality_scores.items():
        for model, score in scores.items():
            quality_data.append({
                'Test': test,
                'Model': model,
                'Quality Score': score
            })
    return pd.DataFrame(quality_data)

# In your main function, update the visualization part:
def create_quality_visualization(quality_df):
    """Create quality score visualization."""
    fig_quality = px.bar(
        quality_df,
        x='Test',
        y='Quality Score',
        color='Model',
        barmode='group',
        title='Quality Score Comparison',
        template="plotly_dark"
    )

    fig_quality.update_layout(
        plot_bgcolor='rgba(30,33,39,1)',
        paper_bgcolor='rgba(30,33,39,1)',
        xaxis_tickangle=-45,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig_quality

def main():
    st.markdown("# 💎 RubyMojo - Local LLM Benchmarks")

    st.markdown("""
    > This dashboard analyzes the performance and accuracy of local LLM models in understanding and generating Ruby programming code.
    >
    > The analysis is based on a test suite of 5 key Ruby programming concepts.
    """)


    # Test Categories
    st.markdown("""
    ### Test Categories:
    1. **Basic Ruby Understanding**: Tests comprehension of fundamental Ruby concepts like modules
    2. **Code Implementation**: Evaluates ability to write functional Ruby classes and methods
    3. **Error Handling**: Assesses understanding of Ruby's error handling mechanisms
    4. **Ruby Best Practices**: Tests knowledge of Ruby naming conventions and best practices
    5. **Advanced Ruby Features**: Evaluates handling of complex features like blocks, procs, and lambdas
    """)

    # Evaluation Methodology
    st.markdown("""
    ### Accuracy Analysis Methodology:
    Each response is evaluated on a 10-point scale based on:
    - Technical accuracy of the content
    - Completeness of the explanation
    - Code correctness and style
    - Proper use of Ruby idioms
    - Error handling and edge cases

    The scores reflect:
    - 9-10: Production-ready, comprehensive response
    - 7-8: Good understanding with minor issues
    - 5-6: Basic understanding with some gaps
    - 3-4: Significant misunderstandings
    - 1-2: Major conceptual errors
    """)

    # Environment Info
    st.markdown("""
    > 🖥️ Test Environment: LM Studio on MacBook Pro (2023)
    > - Apple M2 Pro chip
    > - 16 GB Memory
    > - macOS Sonoma 14.4.1
    """)

    # Models Compared
    st.markdown("""
    ### Models Compared:
    - **Mistral Nemo Instruct** (6.91 GB): A larger model optimized for instruction following
    - **MultiPL-T StarCoderBase** (726.93 MB): A lightweight model focused on programming tasks
    """)

    st.markdown("""
    > More models coming soon...
    """)

    # Load test results
    json_files = glob.glob('*_.json')
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

    # Create tabs with dark theme styling
    tab1, tab2, tab3 = st.tabs(["Performance Analysis", "Accuracy Analysis", "Response Comparison"])

    with tab1:
        st.subheader("Performance Analysis")

        # Response Time Comparison with dark theme
        fig_time = px.bar(
            performance_df,
            x='Test',
            y='Time (s)',
            color='Model',
            barmode='group',
            title='Response Time Comparison',
            template="plotly_dark"
        )
        fig_time.update_layout(
            plot_bgcolor='rgba(30,33,39,1)',
            paper_bgcolor='rgba(30,33,39,1)',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_time, use_container_width=True)

        # Token Usage Comparison with dark theme
        fig_tokens = px.bar(
            performance_df,
            x='Test',
            y='Total Tokens',
            color='Model',
            barmode='group',
            title='Token Usage Comparison',
            template="plotly_dark"
        )
        fig_tokens.update_layout(
            plot_bgcolor='rgba(30,33,39,1)',
            paper_bgcolor='rgba(30,33,39,1)',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_tokens, use_container_width=True)

    quality_scores = get_quality_scores()
    quality_df = create_quality_df(quality_scores)

    with tab2:
        st.subheader("Accuracy Analysis")

        # Create and display quality visualization
        fig_quality = create_quality_visualization(quality_df)
        st.plotly_chart(fig_quality, use_container_width=True)

        # Add explanation of scoring
        st.markdown("""
        ### Scoring Criteria:
        - 9-10: Production-ready, comprehensive response
        - 7-8: Good understanding with minor issues
        - 5-6: Basic understanding with some gaps
        - 3-4: Significant misunderstandings
        - 1-2: Major conceptual errors
        """)

    with tab3:
        st.subheader("Response Comparison")

        # Custom CSS for the response comparison section
        st.markdown("""
            <style>
            .response-container {
                background-color: #1E2127;
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
            }
            .response-header {
                color: #00A4EF;
                font-size: 1.2em;
                margin-bottom: 10px;
            }
            .stSelectbox {
                background-color: #1E2127;
                color: white;
                border-radius: 4px;
                margin-bottom: 20px;
            }
            .stTextArea > div > div {
                background-color: #282C34;
                color: #ABB2BF;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
                border-radius: 4px;
                padding: 10px;
            }
            .stTextArea > div > div:focus {
                border-color: #00A4EF;
                box-shadow: 0 0 0 1px #00A4EF;
            }
            </style>
        """, unsafe_allow_html=True)

        # Test case selection with improved styling
        selected_test = st.selectbox(
            "Select Test Case",
            options=performance_df['Test'].unique(),
            help="Choose a test category to compare model responses"
        )

        # Create two columns for side-by-side comparison
        cols = st.columns(len(results))
        for idx, result in enumerate(results):
            with cols[idx]:
                st.markdown(f"<div class='response-header'>{result['model_name']}</div>", unsafe_allow_html=True)
                test_response = next(
                    test['response']
                    for test in result['data']['tests']
                    if test['test_name'] == selected_test
                )
                st.text_area(
                    "",  # Remove label as we're using custom header
                    value=test_response,
                    height=500,  # Increased height for better readability
                    key=f"response_{idx}",
                    help="Model's response to the selected test case"
                )

    # Footer with social links
    st.markdown("---")
    st.markdown("""
    📝 Created by David Teren

    [![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://x.com/davidteren)
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davidteren/)
    [![Bluesky](https://img.shields.io/badge/Bluesky-0285FF?style=for-the-badge&logo=bluesky&logoColor=white)](https://bsky.app/profile/davidteren.bsky.social)
    [![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/davidteren)
    """)

if __name__ == "__main__":
    main()
