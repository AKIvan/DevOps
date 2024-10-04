import boto3
import argparse
import json
import sys
from operator import itemgetter
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime, timezone
import pprint as pp


class EC2Analyzer:
    """ """

    def __init__(self, region, instance_types):
        self.region = region
        self.instance_types = instance_types
        self.ec2_client = boto3.client("ec2", region_name=region)
        self.specs = {}
        self.prices = {}

    def get_instance_specs(self):
        try:
            response = self.ec2_client.describe_instance_types(
                InstanceTypes=self.instance_types
            )
        except (BotoCoreError, ClientError) as error:
            print(f"Error getting the instance specificaiton: {error}")
            sys.exit(1)

        for instance in response["InstanceTypes"]:
            # print(instance)
            instance_type = instance["InstanceType"]
            vcpus = instance["VCpuInfo"]["DefaultVCpus"]
            # print(instance["MemoryInfo"]["SizeInMiB"])
            memory = instance["MemoryInfo"]["SizeInMiB"] / 1024
            self.specs[instance_type] = {
                "vcpus": vcpus,
                "memory": round(memory, 2),
            }
            # print(self.specs)

    def get_spot_prices(self):
        try:
            response = self.ec2_client.describe_spot_price_history(
                InstanceTypes=self.instance_types,
                # MaxResults=len(self.instance_types),
                ProductDescriptions=["Linux/UNIX"],
                StartTime=datetime.now(timezone.utc),
            )
            pp.pprint(response)
        except (BotoCoreError, ClientError) as error:
            print(f"Error fetching spot prices: {error}")
            sys.exit(1)

        for price_info in response["SpotPriceHistory"]:
            instance_type = price_info["InstanceType"]
            spot_price = float(price_info["SpotPrice"])
            self.prices[instance_type] = spot_price


class CostEffectivenessCalculator:
    def __init__(self, specs, prices):
        self.specs = specs
        self.prices = prices
        self.results = []

    def calculate(self):
        for instance_type in self.specs:
            vcpus = self.specs[instance_type]["vcpus"]
            memory = self.specs[instance_type]["memory"]
            spot_price = self.prices.get(instance_type)
            if spot_price is None:
                print(f"No price available for {instance_type}. Skipping...")
                continue
            total_compute_units = vcpus + memory
            cost_effectiveness = total_compute_units / spot_price
            self.results.append(
                {
                    "InstanceType": instance_type,
                    "vCPUs": vcpus,
                    "Memory (GiB)": memory,
                    "SpotPrice": spot_price,
                    "CostEffectiveness": round(cost_effectiveness, 2),
                }
            )

    def get_ranked_results(self):
        return sorted(self.results, key=itemgetter("CostEffectiveness"), reverse=True)


class EC2SpotInstanceCostEffectivenessTool:
    def __init__(self):
        self.args = self.parse_arguments()
        self.instance_types = self.get_instance_types()
        self.analyzer = EC2Analyzer(self.args.region, self.instance_types)
        self.calculator = None

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Cost Effectiveness Calculator")
        parser.add_argument("--region", required=True, help="AWS Region")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--instance-types",
            nargs="+",
            help="List of EC2 instance types",
        )
        group.add_argument(
            "--instance-file",
            help="Path to JSON file containing instance types",
        )
        return parser.parse_args()

    def get_instance_types(self):
        if self.args.instance_types:
            return self.args.instance_types
        elif self.args.instance_file:
            try:
                with open(self.args.instance_file, "r") as f:
                    instance_types = json.load(f)
                    if not isinstance(instance_types, list):
                        print(
                            "JSON file must contain a list of instance types.\nExample: ['t2.micro','t3.small']"
                        )
                        sys.exit(1)
                    return instance_types
            except Exception as e:
                print(f"Error reading instance types from file: {e}")
                sys.exit(1)
        else:
            print("No instance types provid.")
            sys.exit(1)

    def run(self):
        self.analyzer.get_instance_specs()
        self.analyzer.get_spot_prices()
        self.calculator = CostEffectivenessCalculator(
            self.analyzer.specs, self.analyzer.prices
        )
        self.calculator.calculate()
        results = self.calculator.get_ranked_results()
        self.print_results(results)

    def print_results(self, results):
        print(
            f"{'InstanceType':15} {'vCPUs':5} {'Memory (GiB)':12} {'SpotPrice':10} {'CostEffectiveness':18}"
        )
        print("-" * 65)
        for res in results:
            print(
                f"{res['InstanceType']:15} {res['vCPUs']:5} {res['Memory (GiB)']:12.2f} {res['SpotPrice']:10.4f} {res['CostEffectiveness']:18}"
            )


if __name__ == "__main__":
    tool = EC2SpotInstanceCostEffectivenessTool()
    tool.run()
