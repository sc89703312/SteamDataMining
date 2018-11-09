/**
  * Created by echo on 18/11/5.
  */
import org.apache.spark.SparkConf
import org.apache.spark.SparkContext
import org.apache.spark.graphx._

import scala.util.Random
import org.apache.spark.graphx.util.GraphGenerators
import breeze.linalg.reverse
import breeze.linalg.reverse
import java.io.{File, FileWriter, PrintWriter}

object UserInfluence {
  def sum(xs: Iterable[Double]): Double = {
    xs match {
      case x :: tail => x + sum(tail) // if there is an element, add it to the sum of the tail
      case Nil => 0.0 // if there are no elements, then the sum is 0
    }
  }

  def main(args: Array[String]) {
    val conf = new SparkConf().setAppName("nNeighbours").setMaster("local[4]")
    val sc=new SparkContext(conf)
    sc.setLogLevel("ERROR")


    val sourceId: Double = 3579555650L
    val sourceInf: Double = 5
    val maxIterations: Integer = 2


    @transient
    val verticeWriter = new PrintWriter(new File("/Users/echo/Desktop/vertices.txt"))

    @transient
    val edgeWriter = new PrintWriter(new File("/Users/echo/Desktop/edges.txt"))

    //构建图 顶点Int类型
    val g = GraphLoader.edgeListFile(sc, "/Users/echo/Desktop/relations.txt")
    println("initalGraph:")

    //构建单源点图 计算其他节点到源点的最短距离
    val singleSourceGraph = g.mapVertices((id, _) => if (id == sourceId) sourceInf else Double.NegativeInfinity).mapEdges(_ => 1)
    val shortestGraph = singleSourceGraph.pregel(Double.NegativeInfinity, maxIterations = maxIterations)(
      (id, dist, newDist) => math.max(dist, newDist), // Vertex Program
      triplet => { // Send Message
        if (triplet.srcAttr - triplet.attr > triplet.dstAttr) {
          Iterator((triplet.dstId, triplet.srcAttr - triplet.attr))
        } else {
          Iterator.empty
        }
      },
      (a, b) => math.max(a, b) // Merge Message
    )
    println("shortest path graph:")
//    println(shortestGraph.vertices.filter {case (id, dis) => dis != Double.NegativeInfinity}.count())
//    shortestGraph.vertices.filter {case (id, dis) => dis != Double.NegativeInfinity}.collect.foreach(println(_))

    //根据最短路径图 构建影响力图 计算相邻节点对该节点的影响力贡献
    type VMap=Map[VertexId,Double]
    val newG=shortestGraph.mapVertices((vid,influence)=>Map[VertexId,Double](vid->influence))


    /**
      * 节点数据的更新 就是集合的union
      */
    def vprog(vid:VertexId,vdata:VMap,message:VMap)
    :Map[VertexId,Double]=addMaps(vdata,message)

    /**
      * 发送消息
      */
    def sendMsg(e:EdgeTriplet[VMap, _])={
      if(e.dstAttr.contains(e.srcId) || e.srcAttr(e.srcId) == Double.NegativeInfinity)
        Iterator.empty
      else {
        var tmp: Map[VertexId, Double] = Map()
        tmp += (e.srcId -> e.srcAttr(e.srcId))
        Iterator((e.dstId, tmp))
      }
    }

    /**
      * 消息的合并
      */
    def addMaps(spmap1: VMap, spmap2: VMap): VMap =
      (spmap1.keySet ++ spmap2.keySet).map {
        k => k -> math.min(spmap1.getOrElse(k, Double.MaxValue), spmap2.getOrElse(k, Double.MaxValue))
      }.toMap

    println("Final G")
    val finalG = newG.pregel(Map[VertexId,Double](), 1, EdgeDirection.Out)(vprog, sendMsg, addMaps)
      .mapVertices((cur_id, map) => map.-(cur_id))
//    finalG.vertices.filter {case (id, map) => map.nonEmpty}.collect.foreach {
//      case (id, map) => println((id, map.values.sum))
//    }
    println(finalG.vertices.filter {case (id, map) => map.nonEmpty}.count())

    val subFinalG = finalG.subgraph(vpred = (id, map) => map.nonEmpty)


    subFinalG.vertices.collect.foreach {case (id,map) => verticeWriter.println(id + " " + map.values.sum)}
    subFinalG.triplets.collect.foreach(triplet => edgeWriter.println(triplet.srcId + " " + triplet.dstId))

    edgeWriter.flush()
    verticeWriter.flush()
    edgeWriter.close()
    verticeWriter.close()

  }
}
