import math
import plotly.graph_objects as go
import streamlit as st


def plot_cumulative_success_prob(prob_success, max_trials):
    # Grab your lucky socks and let's plot some success probabilities!
    x_data = list(range(1, max_trials + 1))
    y_data = [1 - (1 - prob_success) ** n for n in x_data]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=x_data, y=y_data, mode="lines+markers", name="Success Curve"),
    )
    fig.update_yaxes(range=[0, 1])
    fig.update_layout(
        title="Your Cumulative Success Story",
        xaxis_title="Number of Tries",
        yaxis_title="Chance of At Least One Win",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("Keep on trying, and the odds will get better!")


def display_results(prob_success, num_trials, cumulative_prob):
    # Who doesn't love a good success story? Here are your stats!
    half_trials = num_trials // 2  # Taking a peek halfway through
    cumulative_prob_half = 1 - (1 - prob_success) ** half_trials

    # When will you hit that sweet 95% success rate? Let's find out!
    num_trials_95 = math.ceil(math.log(1 - 0.95) / math.log(1 - prob_success))

    st.markdown(
        """
        ### Your Probability Breakdown 🎉

        - **Your starting win rate per try**: `{:.2f}%`
        - **Number of tries**: `{}`
        - **Tries needed for a 95% win chance (almost a sure thing!)**: `{}`

        """.format(
            prob_success * 100, num_trials, num_trials_95
        )
    )

    st.markdown("### Key Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Starting Win Rate", value="{:.2f}%".format(prob_success * 100))
    with col2:
        st.metric(
            label="After {} Tries".format(half_trials),
            value="{:.2f}%".format(cumulative_prob_half * 100),
        )
    with col3:
        st.metric(
            label="After {} Tries".format(num_trials),
            value="{:.2f}%".format(cumulative_prob * 100),
        )


def calculate_results(prob_success, num_trials):
    # Crunching the numbers to see how your persistence pays off!
    cumulative_prob = 1 - (1 - prob_success) ** num_trials
    return cumulative_prob


st.title("When Will Success Knock on My Door? 🚪🤔")

st.markdown(
    """
    ## A Little Pep Talk

    Imagine you're job hunting or asking someone out, and it feels like getting a "yes" is as likely as finding a unicorn. Let's say your chances are a slim 10%. Seems daunting, right?

    But here's the cool thing about chance: **the more you try, the better your odds get**. It's not about mindlessly repeating the same move, though. It's about tweaking your game plan based on feedback and keeping at it.

    This little app is here to show you how, even with low odds on a single try, your overall chances of success climb with every new attempt. So even when it feels like the universe is playing hard to get, remember that **a bit of grit and a willingness to keep trying can seriously boost your odds of winning**.
    """
)

# How do you want to roll the dice today? Pick your input style!
input_method = st.radio(
    "Pick Your Data Entry Style", ["Sliders", "Manual Entry", "Fractional Entry"]
)

if input_method == "Sliders":
    prob_success = st.slider("Set Your Single-Try Success Rate", 0.0, 1.0, 0.33)
    num_trials = st.slider("How Many Shots Are You Giving It?", 1, 100, 5)
elif input_method == "Manual Entry":
    prob_success = st.number_input(
        "Type in Your Success Rate per Try",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
    )
    num_trials = st.number_input(
        "And How Many Tries Are You Up For?", min_value=1, max_value=1000000, value=10
    )
else:
    numerator = st.number_input("Number of Wins", min_value=0, value=1)
    denominator = st.number_input("Out of How Many Tries?", min_value=1, value=7)
    prob_success = numerator / denominator if denominator != 0 else 0
    num_trials = st.number_input(
        "Total Tries You're Going For", min_value=1, max_value=1000000, value=10
    )

# Let's see those odds increase with every try!
plot_cumulative_success_prob(prob_success, num_trials)

cumulative_prob = calculate_results(prob_success, num_trials)

# And now, for the grand reveal of your chances!
display_results(prob_success, num_trials, cumulative_prob)
