// Create a text parameter named DataPath containing the full requests.csv path.
let
    Source = Csv.Document(File.Contents(DataPath),[Delimiter=",",Columns=12,Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    BlankDates = Table.ReplaceValue(Headers,"",null,Replacer.ReplaceValue,{"closed_date"}),
    Typed = Table.TransformColumnTypes(BlankDates,{
        {"ticket_id",type text},{"created_date",type date},{"closed_date",type date},
        {"domain",type text},{"priority",type text},{"owner_team",type text},{"status",type text},
        {"sla_days",Int64.Type},{"age_or_cycle_days",Int64.Type},{"closed_flag",Int64.Type},
        {"on_time_flag",Int64.Type},{"overdue_flag",Int64.Type}},"en-US")
in
    Typed
