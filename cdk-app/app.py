#!/usr/bin/env python3

from aws_cdk import core

from titanic_pipeline.titanic_pipeline_stack import TitanicPipelineStack

app = core.App()
TitanicPipelineStack(
    app,
    "TitanicPipelineAppStack",
)

app.synth()
