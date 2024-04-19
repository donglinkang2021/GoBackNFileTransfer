from visualize import get_dataframe_log, plot_log

log_file = 'sender.log'
df_log = get_dataframe_log(log_file)
df_log.head()

figsize = (40, 10)
save_dir = 'plots'
attributes = ['status', 'action', 'pdu_type']
show_values = ['data_size', 'frame_no']
for show_value in show_values:
    for attribute in attributes:
        plot_log(df_log, attribute, show_value, save_dir, True, figsize[0], figsize[1])


# generate a report.md file here
content = f"# Report\n\n"

# # write a table
# content += "| Attribute | Data Size | Frame No. / Ack No. |\n"
# content += "| --------- | --------- | ------------------- |\n"
# for attribute in attributes:
#     data_size_path = f"{save_dir}/{attribute}_data_size.png" 
#     frame_no_path = f"{save_dir}/{attribute}_frame_no.png"
#     content += f"| **{attribute}** | ![plot]({data_size_path}) | ![plot]({frame_no_path}) |\n"


# write a table
content += "## Details\n\n"

for attribute in attributes:

    content += f"### {attribute.upper()}\n\n"

    for show_value in show_values:
        content += f"#### {show_value}\n\n"
        plot_path = f"{save_dir}/{attribute}_{show_value}.png"
        content += f"![plot]({plot_path})\n\n"

report_file = 'report.md'
with open(report_file, 'w') as file:
    file.write(content)